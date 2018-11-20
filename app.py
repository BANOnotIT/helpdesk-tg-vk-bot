import logging

from flask import Flask, request

import db
from api import TgApi, VkApi
from bot_brains import process_nmessage
from config import *

app = Flask(__name__)
tg_api = TgApi(tg_token)
vk_api = VkApi(vk_token)

# Инициализируем все таблички в бд
db.create_tables()


@app.before_request
def before_request():
    db.database.connect(reuse_if_open=True)


@app.teardown_appcontext
def teardown_appcontext(*args):
    db.database.close()


# Логируем все что у нас есть в gunicorn, чтобы было видно в консоли
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    # Учитываем уровень логов самого gunicorn
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/')
def hello_world():
    return 'Hello World!'


# Обрабатываем телеграмовы сообщения
@app.route('/telegram-handler', methods=['POST'])
def telegram():
    json = request.get_json()

    if json.get('message'):
        message = tg_api.get_nmessage(json['message'])
        app.logger.info('Telegram message: {}'.format(message.__repr__()))
        process_nmessage(message)

    return 'Ok'


# Обрабатываем телеграмовы сообщения
@app.route('/vkontakte-handler', methods=['POST'])
def vkontakte():
    json = request.get_json()

    app.logger.info(repr(json))

    if json['type'] == 'confirmation':
        return vk_domain_verify_salt

    message = vk_api.get_nmessage(json)
    app.logger.info('Vkontakte message: {}'.format(message.__repr__()))
    process_nmessage(message)

    return 'Ok'


if __name__ == '__main__':
    app.run()
