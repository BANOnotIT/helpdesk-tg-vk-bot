from enum import Enum


class Api:
    def get_nmessage(self, message: dict):
        raise TypeError('Unimplemented method `get_nmessage` in Api')

    def message(self, to: str, message: str):
        raise TypeError('Unimplemented method `message` in Api')


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
    chat = None

    def reply(self, message: str):
        raise TypeError('Unimplemented method `message` in NMessage')

    def __repr__(self):
        return '<Message {} from {}: {}>'.format(self.kind.name, self.user.__repr__(), self.text)
