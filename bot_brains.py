from flask import current_app

from api import Message, EMessageType as MsgType, EPlatform
from config import *
from db import EUserState, User
from state_machine import State, Machine
from utils import get_random_phrase


class InitialState(State):
    def transition_rule(self, msg):
        return AuthorizingState()


class AuthorizingState(State):
    def transition_rule(self, msg: Message):
        if 'heizenberg' in msg.text.lower() or msg.kind is MsgType.command and msg.text == '/cancel':
            return BaseState()

        return None

    def leave(self, msg: Message):
        # Отвечаем пользователю
        msg.reply('You\'re goddamn right! Now let\'s work!')

    def enter(self, msg: Message):
        # Переводим нашего пользователя в статус авторизации
        msg.user.set_state(EUserState.authorizing)
        msg.user.save()

        # Приветствуем пользователя и сразу говорим, что он должен пройти обряд инициализации
        msg.reply('I\'m the cook. I\'m the man who killed Gus Fring. Say my name.')

    def stay(self, msg: Message):
        # Переход не случился
        msg.reply('You know how exactly I am. Now say my name.')


class BaseState(State):
    def transition_rule(self, msg: Message):
        command = msg.kind is MsgType.command

        if command and msg.text == '/bind':
            return BindTGState() if msg.platform is EPlatform.vk else BindVKState()

        return None

    def enter(self, msg: Message):
        user = msg.user
        user.set_state(EUserState.base)
        user.save()

    def stay(self, msg: Message):
        if msg.kind is MsgType.command and msg.text.startswith('/in '):
            self.in_command_handler(msg)
            return

        msg.reply('What do you want from me?')

    def in_command_handler(self, msg: Message):
        is_from_vk = msg.platform is EPlatform.vk
        # Пропускаем первые 4 символа, обозначающие команду ("/in "), и берём остальное сообщение
        phrase = msg.text[4:].strip()

        # Берём нашего пользователя
        n_user = User.get_or_none(User.state_param == phrase)

        current_app.logger.info('Trying phrase "{}"'.format(phrase))

        # Скорее всего такого пользователя нет, ну или фраза неправильная
        if n_user is None:
            msg.reply('I don\'n know what you\'re talking about.')
            return

        # Производим слияние двух аккаунтов в один (суммируем деньги, переводим друзей, etc.)
        if is_from_vk:
            msg.user.tg = n_user.tg
        else:
            msg.user.vk = n_user.vk

        # Теперь нам прошлый аккаунт не нужен 
        # Удаляем, чтобы не создавать дублей в бд
        n_user.delete_instance()

        # Ну и теперь уже сохраняем текущего пользователя
        msg.user.save(force_insert=True)  # обязательно указываем force_insert, потому что мы поменяли ключевые поля

        # Теперь говорим пользователю, что же изменилось
        msg.reply('Alright. Now I can talk to you in various kinds!')

        # Обязательно говорим, что кто-то совершил интеграцию
        current_app.logger.info('{} integrated {}'.format(repr(msg.user), 'tg' if is_from_vk else 'vk'))


binding_msg = (
    'Go to {}.\n'
    'When I\'ll have no doubt you are a good person to work with say\n'
    '\n'
    '/in {}\n'
    '\n'
    'Then I would be sure you have both channels to contact me, ok?'
)


class BindVKState(State):
    def transition_rule(self, msg: Message):
        if MsgType.command and msg.text == '/cancel':
            return BaseState()

        return None

    def leave(self, msg: Message):
        # Отвечаем пользователю
        msg.reply('Ok. I\'ll say to my boys that it\'s unnecessary')

    def enter(self, msg: Message):
        # Выбираем случайные 4 слова откуда-либо, главное случайные
        phrase = get_random_phrase().lower()

        # Меняем состояние машины и передаём дополнительный аргумент к состоянию
        msg.user.set_state(EUserState.integrating_vk, phrase)
        msg.user.save()

        # Передаём пользователю инструкцию по интегрированию нового сервиса
        msg.reply(binding_msg.format(vk_link, phrase))

    def stay(self, msg: Message):
        # Переход не случился
        msg.reply('I\'m waiting for you in other info channel. You only can /cancel it.')


class BindTGState(BindVKState):
    # В чём же прелесть ООП? В том, что не нужно копировать один и тот же код 1000 раз.
    def enter(self, msg: Message):
        # Выбираем случайные 4 слова откуда-либо, главное случайные
        phrase = get_random_phrase().lower()

        # Меняем состояние машины и передаём дополнительный аргумент к состоянию
        msg.user.set_state(EUserState.integrating_tg, phrase)
        msg.user.save()

        # Передаём пользователю инструкцию по интегрированию нового сервиса
        msg.reply(binding_msg.format(tg_link, phrase))


class BotStateMachine(Machine):
    map_states = {
        EUserState.initial: InitialState(),
        EUserState.authorizing: AuthorizingState(),
        EUserState.integrating_vk: BindVKState(),
        EUserState.integrating_tg: BindTGState(),
    }

    def get_initial_state(self, msg):
        state = EUserState(msg.user.state)

        if state in self.map_states:
            return self.map_states.get(state)

        return BaseState()


machine = BotStateMachine()


def process_nmessage(message: Message):
    machine.run(message)
