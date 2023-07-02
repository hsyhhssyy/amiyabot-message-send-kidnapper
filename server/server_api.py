import base64
import hmac
import os

from peewee import SelectQuery
from datetime import datetime,timedelta

from core import app

from amiyabot.network.httpServer import BaseModel

from ..utils.logger import log

from ..database.message import AmiyaBotMessageKidnapperMessageDataBase

@app.controller
class Kidnapper:
    @app.route(method='post')
    async def getMessage(self):
        
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
    
        # 查询task
        query = (AmiyaBotMessageKidnapperMessageDataBase
                .select()
                .where(AmiyaBotMessageKidnapperMessageDataBase.create_at > five_minutes_ago))
        
        result_dicts = []
        for result in query:
            result_dict = {
                "id": result.id,
                "uuid": result.uuid,
                "channel_id": result.channel_id,
                "user_id": result.user_id,
                "type": result.type,
                "data": result.data,
                "create_at": result.create_at,
            }

            if result.type == "Image":
                with open(result.data, 'rb') as file:
                    img_bytes = file.read()
                    img_base64 = base64.b64encode(img_bytes).decode()
                    result_dict["data"] = img_base64

            result_dicts.append(result_dict)

        return app.response({"success": True, "messages": result_dicts})