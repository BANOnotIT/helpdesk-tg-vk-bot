from enum import Enum, unique

from peewee import Model, IntegerField, PostgresqlDatabase, TextField, CompositeKey
from urllib3.util import parse_url

from config import *


def get_database():
    parsed_url = parse_url(db_url)

    # Берём из auth имя пользователя и пароль от БД
    username, password = parsed_url.auth.split(':')

    return PostgresqlDatabase(
        parsed_url.path[1:],  # Пропускаем первый "/", так как он не является названием БД
        host=parsed_url.host,
        user=username,
        password=password
    )


database = get_database()


@unique
class EUserState(Enum):
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
    tg = IntegerField(default=0, help_text='Telegram User Id')
    vk = IntegerField(default=0, help_text='VK User Id')
    state = IntegerField(default=EUserState.initial.value, choices=EUserState.as_choices(),
                         help_text='Current bot state for user')
    state_param = TextField(default='', help_text='Param for state')

    def set_state(self, state: EUserState, param=''):
        self.state = state.value
        self.state_param = param

    def __repr__(self):
        return '<User tg={} vk={} state={}:{}>'.format(self.tg, self.vk, EUserState(self.state).name,
                                                       self.state_param)

    class Meta:
        database = database
        table_name = 'app_users'
        primary_key = CompositeKey('tg', 'vk')


def create_tables():
    with database:
        database.create_tables([User])
    # закрываем подключение, чтобы не могли слушать ничего страшного.
    database.close()
