from enum import Enum

from db import User


class Api:
    def get_nmessage(self, message):
        raise TypeError('Unimplemented method message in Api')


class MessageTypeEnum(Enum):
    unknown = 0
    text = 1
    command = 2
    joined = 3
    leaved = 4


class NMessage:
    text = ''
    kind = MessageTypeEnum.unknown
    user = None  # User

    def reply(self, message: str):
        raise TypeError('Unimplemented method message in Api')

    def __repr__(self):
        return '<Message {} from {}: {}>'.format(self.kind.name, self.user, self.text)


class TgApi(Api):
    token = ''

    def __init__(self, token):
        self.token = token

    def get_nmessage(self, message):
        user = User.get_or_none(tg=int(message['from']['id']))
        if not user:
            user = User.create()
            user.tg = int(message['from']['id'])
            user.save()

        kind = TgMessage.get_kind(message)
        return TgMessage(message.get('text', ''), user, self, kind)


class TgMessage(NMessage):
    def __init__(self, text, user, api, kind):
        self.api = api
        self.text = text
        self.user = user
        self.kind = kind

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
