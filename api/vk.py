from flask import current_app
from requests import post

from db import User
from .base import Api, EMessageType, Message, EPlatform


class VkApi(Api):
    token = ''
    url = 'https://api.vk.com/method/'

    def __init__(self, token):
        self.token = token
        self.url = self.url.format(token)

    def get_nmessage(self, message):

        vk_id = 0
        kind = EMessageType.unknown
        text = ''

        # Если появился новый пользователь или начался новый диалог
        if message['type'] in ('group_join', 'message_allow'):
            vk_id = message['object']['user_id']
            kind = EMessageType.joined

        # Если мы узнали, что пользователь покинул нас...
        elif message['type'] == 'group_leave':
            vk_id = message['object']['user_id']
            kind = EMessageType.leaved

        # Если пользователь прислал нам сообщение
        elif message['type'] in ('message_new', 'message_edit'):
            vk_id = message['object']['from_id']
            text = message['object']['text']
            kind = EMessageType.command if text.startswith('/') else EMessageType.text

        user, new = User.get_or_create(vk=vk_id)

        if new:
            current_app.logger.info('Created new vk user: {}'.format(repr(user)))

        message = VkMessage(text, user, kind, vk_id)
        message.api = self

        return message

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


class VkMessage(Message):
    platform = EPlatform.vk
    api = None

    def reply(self, message: str):
        return self.api.message(self.chat, message)
