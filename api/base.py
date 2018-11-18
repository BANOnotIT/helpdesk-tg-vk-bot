from enum import Enum


class Api:
    def get_nmessage(self, message: dict):
        raise TypeError('Unimplemented method `get_nmessage` in Api')

    def message(self, to: str, message: str):
        raise TypeError('Unimplemented method `message` in Api')


class MessageType(Enum):
    unknown = 0
    text = 1
    command = 2
    joined = 3
    leaved = 4


class Platform(Enum):
    unknown = 0
    tg = 1
    vk = 2


class NMessage:
    text = ''
    kind = MessageType.unknown
    user = None  # User
    chat = None
    platform = Platform.unknown

    def reply(self, message: str):
        raise TypeError('Unimplemented method `message` in NMessage')

    def __repr__(self):
        return '<Message {} from {}: {}>'.format(self.kind.name, self.user.__repr__(), self.text)
