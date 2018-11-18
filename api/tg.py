from requests import post

from db import User
from .base import Api, NMessage, MessageTypeEnum


class TgApi(Api):
    token = ''
    url = 'https://api.telegram.org/bot{}/'

    def __init__(self, token):
        self.token = token
        self.url = self.url.format(token)

    def get_nmessage(self, message):
        user = User.get_or_none(tg=int(message['from']['id']))
        if not user:
            user = User.create()
            user.tg = int(message['from']['id'])
            user.save()

        chat = int(message['chat']['id'])

        kind = TgMessage.get_kind(message)
        return TgMessage(message.get('text', ''), user, self, kind, chat)

    def exec(self, method: str, data: dict):
        return post(self.url + method, data).json()

    def message(self, chat: int, message: str):
        return self.exec('sendMessage', {
            'chat_id': chat,
            'text': message,
        })


class TgMessage(NMessage):
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
                return MessageTypeEnum.command

            else:
                return MessageTypeEnum.text

        elif message.get('new_chat_member'):
            return MessageTypeEnum.joined

        elif message.get('left_chat_member'):
            return MessageTypeEnum.leaved

        else:
            return MessageTypeEnum.unknown

    def reply(self, message: str):
        return self.api.message(self.chat, message)
