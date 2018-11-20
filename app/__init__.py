import logging

from flask import Flask, request

from config import *
from .api import TgApi, VkApi
from .core import process_nmessage
from .db import create_tables, database

flask_app = Flask(__name__)
tg_api = TgApi(tg_token)
vk_api = VkApi(vk_token)

# Инициализируем все таблички в бд
create_tables()


@flask_app.before_request
def before_request():
    database.connect(reuse_if_open=True)


@flask_app.teardown_appcontext
def teardown_appcontext(*args):
    database.close()


# Логируем все что у нас есть в gunicorn, чтобы было видно в консоли
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    flask_app.logger.handlers = gunicorn_logger.handlers
    # Учитываем уровень логов самого gunicorn
    flask_app.logger.setLevel(gunicorn_logger.level)


@flask_app.route('/')
def hello_world():
    return 'Hello World!'


# Обрабатываем телеграмовы сообщения
@flask_app.route('/telegram-handler', methods=['POST'])
def telegram():
    json = request.get_json()

    if json.get('message'):
        message = tg_api.get_message(json['message'])
        flask_app.logger.info('Telegram message: {}'.format(message.__repr__()))
        process_nmessage(message)

    return 'Ok'


# Обрабатываем телеграмовы сообщения
@flask_app.route('/vkontakte-handler', methods=['POST'])
def vkontakte():
    json = request.get_json()

    flask_app.logger.info(repr(json))

    if json['type'] == 'confirmation':
        return vk_domain_verify_salt

    message = vk_api.get_message(json)
    flask_app.logger.info('Vkontakte message: {}'.format(message.__repr__()))
    process_nmessage(message)

    return 'Ok'


if __name__ == '__main__':
    flask_app.run()
