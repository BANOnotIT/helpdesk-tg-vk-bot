import os
from enum import Enum, unique

from peewee import Model, IntegerField, PostgresqlDatabase, TextField

database = PostgresqlDatabase(os.getenv('DATABASE'))


class BaseModel(Model):
    class Meta:
        database = database


@unique
class UserState(Enum):
    authorizing = 1
    base = 2
    integrating_tg = 3
    integrating_vk = 4
    trading = 5

    @classmethod
    def as_choices(cls):
        return [reversed(item) for item in cls.__members__.items()]


class User(BaseModel):
    tg_id = IntegerField(null=True, unique=True, help_text='Telegram User Id')
    vk_id = IntegerField(null=True, unique=True, help_text='VK User Id')
    state = IntegerField(default='creating', choices=UserState.as_choices())
    additional_parameter = TextField()


def create_tables():
    with database:
        database.create_tables([User])
