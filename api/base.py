from enum import Enum


class Api:
    def get_message(self, message: dict):
        raise NotImplementedError()

    def message(self, to: str, message: str):
        raise NotImplementedError()


class EMessageType(Enum):
    unknown = 0
    text = 1
    command = 2
    joined = 3
    leaved = 4


class EPlatform(Enum):
    unknown = 0
    tg = 1
    vk = 2


class Message:
    text = ''
    kind = EMessageType.unknown
    user = None  # User
    chat = None
    platform = EPlatform.unknown

    def __init__(self, text, user, kind, chat):
        self.text = text
        self.user = user
        self.kind = kind
        self.chat = chat

    def reply(self, message: str):
        raise NotImplementedError()

    def __repr__(self):
        return '<Message {} from {}: {}>'.format(self.kind.name, self.user.__repr__(), self.text)
