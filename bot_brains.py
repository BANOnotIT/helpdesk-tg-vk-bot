from logging import info

from api import NMessage, MessageTypeEnum as MsgType
from db import UserState


def process_nmessage(message: NMessage):
    user = message.user
    state = UserState(user.state)

    info('Processing user {}', user.__repr__())
    info('User state is authorizing {}', UserState.initial is state)

    cancel = message.kind is MsgType.command and message.text == '/cancel'

    if state is UserState.initial:
        user.state = UserState.authorizing.value
        user.state_param = ''
        user.save()

        info('Sending auth message')

        resp = message.reply('I\'m the cook. I\'m the man who killed Gus Fring. Say my name.')

        info(repr(resp))

    elif state is UserState.authorizing:
        # Проверяем, есть ли переход в другое состояние машины
        if 'heizenberg' in message.text.lower() or cancel:
            # Меняем состояние машины
            user.state = UserState.base.value
            user.state_param = ''
            user.save()

            # Отвечаем пользователю
            message.reply('You\'re goddamn right! Now let\'s work!')

        else:
            # Переход не случился
            message.reply('You know how exactly I am. Now say my name.')
