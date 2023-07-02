from datetime import datetime

from peewee import AutoField,CharField,TextField,DateTimeField,BlobField

from amiyabot.database import ModelClass

from core.database.plugin import db

class AmiyaBotMessageKidnapperMessageDataBase(ModelClass):
    id: int = AutoField()
    uuid: str = CharField()
    channel_id: str = CharField()
    user_id: str = CharField()
    type: str = CharField()
    data: str = TextField()
    create_at: datetime = DateTimeField(null=True)

    class Meta:
        database = db
        table_name = "amiyabot-message-kidnapper-messages"