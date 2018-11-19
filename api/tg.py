from flask import current_app
from requests import post

from db import User
from .base import Api, MessageType, Message, Platform


class TgApi(Api):
    token = ''
    url = 'https://api.telegram.org/bot{}/'

    def __init__(self, token):
        self.token = token
        self.url = self.url.format(token)

    @staticmethod
    def get_message_kind(message):
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

    def get_nmessage(self, message):
        user, new = User.get_or_create(tg=int(message['from']['id']))

        if new:
            current_app.logger.info('Created new tg user: {}'.format(repr(user)))

        chat = int(message['chat']['id'])
        kind = self.get_message_kind(message)

        message = TgMessage(message.get('text', ''), user, kind, chat)
        message.api = self

        return message

    def exec(self, method: str, data: dict):
        return post(self.url + method, data).json()

    def message(self, chat: int, message: str):
        current_app.logger.debug('Sending tg message to {}: {}'.format(chat, message))
        return self.exec('sendMessage', {
            'chat_id': chat,
            'text': message,
        })


class TgMessage(Message):
    platform = Platform.tg
    api = None

    def reply(self, message: str):
        return self.api.message(self.chat, message)
