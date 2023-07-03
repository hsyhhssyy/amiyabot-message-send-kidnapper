import os
import uuid
import types

from datetime import datetime

from amiyabot import Message, Chain, log
from amiyabot.adapters.cqhttp import CQHttpBotInstance
from amiyabot.builtin.messageChain.element import Text, At, Image, Html

from core.customPluginInstance import AmiyaBotPluginInstance

from .utils.logger import log
from .database.message import AmiyaBotMessageKidnapperMessageDataBase
from .server import server_api # 必须执行这个空引入来引入服务器代码

curr_dir = os.path.dirname(__file__)

class MessageSendKidnapperPluginInstance(AmiyaBotPluginInstance):
    def install(self):
        AmiyaBotMessageKidnapperMessageDataBase.create_table(safe=True)


bot = MessageSendKidnapperPluginInstance(
    name='输出重定向',
    version='1.0',
    plugin_id='amiyabot-message-send-kidnapper',
    plugin_type='',
    description='将Adaper的发送消息拦截到数据库中。',
    document=f'{curr_dir}/README.md'

)

temp_dir = f"{curr_dir}/../../resource/message-kidnapper"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

old_message_func = {}


async def custom_send_chain_message(self, chain, use_http=False, *args, **kwargs):

    processable_instances = [chain_data for chain_data in chain.chain if
                             (isinstance(chain_data, Text)
                              or isinstance(chain_data, At)
                              or isinstance(chain_data, Image)
                              or isinstance(chain_data, Html))]
    other_instances = [
        chain_data for chain_data in chain.chain if chain_data not in processable_instances]

    if len(processable_instances) > 0:

        for chain_data in processable_instances:
            new_uuid = uuid.uuid4()

            if isinstance(chain_data, Text):
                if chain_data.content != "":
                    AmiyaBotMessageKidnapperMessageDataBase.create(
                        uuid=new_uuid,
                        channel_id=chain.data.channel_id,
                        type="Text",
                        data=chain_data.content,
                        create_at=datetime.now()
                    )
                    log.info(f'Created a new message with UUID: {new_uuid}')
            if isinstance(chain_data, At):
                if chain_data.target != "":
                    AmiyaBotMessageKidnapperMessageDataBase.create(
                        uuid=new_uuid,
                        channel_id=chain.data.channel_id,
                        type="At",
                        data=chain_data.target,
                        create_at=datetime.now()
                    )
            if isinstance(chain_data, Image):
                img_content = await chain_data.get()
                if isinstance(img_content, bytes):

                    file_path = f'{temp_dir}/{new_uuid}.png'
                    with open(file_path, 'wb') as file:
                        file.write(img_content)

                    AmiyaBotMessageKidnapperMessageDataBase.create(
                        uuid=new_uuid,
                        channel_id=chain.data.channel_id,
                        type="Image",
                        data=file_path,
                        create_at=datetime.now()
                    )
                else:
                    log.info(f'Wrong Img Type:{img_content}')

            if isinstance(chain_data, Html):
                img_content = await chain_data.create_html_image()
                if isinstance(img_content, bytes):

                    file_path = f'{temp_dir}/{new_uuid}.png'
                    with open(file_path, 'wb') as file:
                        file.write(img_content)

                    AmiyaBotMessageKidnapperMessageDataBase.create(
                        uuid=new_uuid,
                        channel_id=chain.data.channel_id,
                        type="Image",
                        data=file_path,
                        create_at=datetime.now()
                    )

        AmiyaBotMessageKidnapperMessageDataBase.create(
            uuid=uuid.uuid4(),
            channel_id=chain.data.channel_id,
            type="MessageBreak",
            data="",
            create_at=datetime.now()
        )

    if len(other_instances) > 0:
        msg_types = [type(chain_data).__name__ for chain_data in other_instances]
        log.info(f'Elements leaked to adapter: {msg_types}')
        chain.chain = other_instances
        func = old_message_func.get(self)
        if func is not None:
            return await func(chain, use_http)


@bot.message_before_handle
async def _(data: Message, factory_name: str, instance):
    if isinstance(instance, CQHttpBotInstance):
        if instance not in old_message_func:
            old_message_func[instance] = instance.send_chain_message
            instance.send_chain_message = types.MethodType(
                custom_send_chain_message, instance)
