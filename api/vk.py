from flask import current_app
from requests import post

from db import User
from .base import Api, MessageType, NMessage


class VkApi(Api):
    token = ''
    url = 'https://api.vk.com/method/'

    def __init__(self, token):
        self.token = token
        self.url = self.url.format(token)

    def get_nmessage(self, message):

        vk_id = 0
        kind = MessageType.unknown
        text = ''

        # Если появился новый пользователь или начался новый диалог
        if message['type'] in ('group_join', 'message_allow'):
            vk_id = message['object']['user_id']
            kind = MessageType.joined

        # Если мы узнали, что пользователь покинул нас...
        elif message['type'] == 'group_leave':
            vk_id = message['object']['user_id']
            kind = MessageType.leaved

        # Если пользователь прислал нам сообщение
        elif message['type'] in ('message_new', 'message_edit'):
            vk_id = message['object']['from_id']
            text = message['object']['text']
            kind = MessageType.command if text.startswith('/') else MessageType.text

        user, new = User.get_or_create(vk=vk_id)

        if new:
            current_app.logger.info('Created new vk user: {}'.format(repr(user)))

        return VkMessage(text, user, self, kind, vk_id)

    def exec(self, method: str, data: dict):
        settings = {
            'access_token': self.token,
            'v': '5.87'
        }

        return post(self.url + method, {**data, **settings}).json()

    def message(self, chat: int, message: str):
        current_app.logger.debug('Sending vk message to {}: {}'.format(chat, message))
        return self.exec('messages.send', {
            'user_id': chat,
            'message': message,
        })


class VkMessage(NMessage):
    def __init__(self, text, user, api, kind, chat):
        self.api = api
        self.text = text
        self.user = user
        self.kind = kind
        self.chat = chat

    def reply(self, message: str):
        return self.api.message(self.chat, message)
