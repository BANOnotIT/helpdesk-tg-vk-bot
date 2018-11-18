from flask import current_app

from api import NMessage, MessageType as MsgType, Platform
from db import UserState, User
from utils import get_random_phrase

# Ссылки на нашего бота в разных системах
tg_link = 'https://t.me/itsolschool_heizenberg_bot'
vk_link = 'https://vk.com/im?sel=-174147611'


def process_nmessage(message: NMessage):
    # Переменные для удобства
    user = message.user
    state = UserState(user.state)
    is_from_vk = message.platform is Platform.vk

    # Пользователь пожелал отменить текущее действие
    cancel = message.kind is MsgType.command and message.text == '/cancel'

    # Пользователь пришёл в первый раз и вообще это его первое сообщение
    if state is UserState.initial:
        # Переводим нашего пользователя в статус авторизации
        user.set_state(UserState.authorizing)
        user.save()

        # Приветствуем пользователя и сразу говорим, что он должен пройти обряд инициализации
        message.reply('I\'m the cook. I\'m the man who killed Gus Fring. Say my name.')

    elif state is UserState.authorizing:
        # Проверяем, есть ли переход в другое состояние машины
        if 'heizenberg' in message.text.lower() or cancel:
            # Меняем состояние "машины" для этого конкретного пользователя
            user.set_state(UserState.base)
            user.save()

            # Отвечаем пользователю
            message.reply('You\'re goddamn right! Now let\'s work!')

            # Логируем, что в нашем полку прибыло
            current_app.logger.info('Authorization succeeded: {}'.format(repr(user)))

        else:
            # Переход не случился
            message.reply('You know how exactly I am. Now say my name.')

    # Основные состояния бота
    elif state is UserState.base:
        # Обрабатываем команды
        if message.kind is MsgType.command:

            # Пользователь изъявил желание интегрироваться ещё с чем-то
            if message.text == '/bind':
                # Получаем ссылку на бота в разных системах
                link = tg_link if is_from_vk else vk_link

                # Выбираем случайные 4 слова откуда-либо, главное случайные
                phrase = get_random_phrase().lower()

                # Меняем состояние машины и передаём дополнительный аргумент к состоянию
                user.set_state(UserState.integrating_vk, phrase)
                user.save()

                # Передаём пользователю инструкцию по интегрированию нового сервиса
                message.reply('''
                Go to {}.
                When I'll have no doubt you are a good person to work with say `/in {}`. 
                Then I would be sure you have both channels to contact me, ok?
                '''.format(link, phrase))

            # Обработка привязки одного аккаунта с другим
            elif message.text.startswith('/in'):

                # Пропускаем первые 4 символа, обозначающие команду ("/in "), и берём остальное сообщение
                phrase = message.text[3:]

                # Нужно чётко знать, какого пользователя мы ищем, чтобы не удалить случайно другого.
                # Наш не занимается ничем иным кроме ожидания интеграции
                user_integrating_vk = (User.tg != 0) & \
                                      (User.vk == 0) & \
                                      (User.state == UserState.integrating_vk.value)

                user_integrating_tg = (User.vk != 0) & \
                                      (User.tg == 0) & \
                                      (User.state == UserState.integrating_tg.value)

                # Берём нашего пользователя
                n_user = User.get_or_none(
                    # user_integrating_tg if is_from_vk else user_integrating_vk,
                    state_param=phrase
                )

                # Скорее всего такого пользователя нет, ну или фраза неправильная
                if n_user is None:
                    message.reply('I don\'n know what you\'re talking about.')
                    return

                # Производим слияние двух аккаунтов в один (суммируем деньги, переводим друзей, etc.)
                if is_from_vk:
                    user.tg = n_user.tg
                else:
                    user.vk = n_user.vk

                # Теперь нам прошлый аккаунт не нужен, чтобы не создавать дублей в бд
                n_user.delete_instance()

                # Ну и теперь уже сохраняем текущего пользователя
                user.save()

                # Обязательно говорим, что кто-то совершил интеграцию
                current_app.logger.info(
                    '{} integrated {}'.format(
                        repr(user),
                        'tg' if is_from_vk else 'vk'
                    )
                )
