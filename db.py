import os
from enum import Enum, unique

from peewee import Model, IntegerField, PostgresqlDatabase, TextField
from urllib3.util import parse_url

db_url = parse_url(os.getenv('DATABASE_URL'))

# Берём из auth имя пользователя и пароль от БД
username, password = db_url.auth.split(':')

database = PostgresqlDatabase(
    db_url.path[1:],  # Пропускаем первый "/", так как он не является названием БД
    host=db_url.host,
    user=username,
    password=password
)


@unique
class UserState(Enum):
    initial = 0
    authorizing = 1
    base = 2
    integrating_tg = 3
    integrating_vk = 4
    trading = 5

    @classmethod
    def as_choices(cls):
        return [(item[1].value, item[0]) for item in cls.__members__.items()]


class User(Model):
    tg = IntegerField(null=True, help_text='Telegram User Id')
    vk = IntegerField(null=True, help_text='VK User Id')
    state = IntegerField(default=UserState.initial.value, choices=UserState.as_choices())
    state_param = TextField(default='')

    def __repr__(self):
        return '<User tg={} vk={} state={}:{}>'.format(self.tg, self.vk, UserState(self.state).name,
                                                       self.state_param)

    class Meta:
        database = database
        table_name = 'app_users'
        primary_key = False


def create_tables():
    with database:
        database.create_tables([User])
