from logging import debug

from flask import current_app
from requests import post

from db import User
from .base import Api, NMessage, MessageType, Platform


class TgApi(Api):
    token = ''
    url = 'https://api.telegram.org/bot{}/'

    def __init__(self, token):
        self.token = token
        self.url = self.url.format(token)

    def get_nmessage(self, message):
        user, new = User.get_or_create(tg=int(message['from']['id']))

        if new:
            current_app.logger.info('Created new tg user: {}'.format(repr(user)))

        chat = int(message['chat']['id'])

        kind = TgMessage.get_kind(message)
        return TgMessage(message.get('text', ''), user, self, kind, chat)

    def exec(self, method: str, data: dict):
        return post(self.url + method, data).json()

    def message(self, chat: int, message: str):
        debug('Sending tg message to {}: {}'.format(chat, message))
        return self.exec('sendMessage', {
            'chat_id': chat,
            'text': message,
        })


class TgMessage(NMessage):
    platform = Platform.tg

    def __init__(self, text, user, api, kind, chat):
        self.api = api
        self.text = text
        self.user = user
        self.kind = kind
        self.chat = chat

    @staticmethod
    def get_kind(message):
        if message.get('text'):
            if message['text'].startswith('/'):
                return MessageType.command

            else:
                return MessageType.text

        elif message.get('new_chat_member'):
            return MessageType.joined

        elif message.get('left_chat_member'):
            return MessageType.leaved

        else:
            return MessageType.unknown

    def reply(self, message: str):
        return self.api.message(self.chat, message)
