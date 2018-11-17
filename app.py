import logging

from flask import Flask, request

import db
from api import TgApi

app = Flask(__name__)
tg_api = TgApi('SomeToken')

# Инициализируем все таблички в бд
db.create_tables()

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
    app.logger.info('Telegram updates: {}'.format(json.__repr__()))
    if json.get('message'):
        message = tg_api.get_nmessage(json['message'])
        app.logger.info('Telegram message: {}'.format(message.__repr__()))

    return 'Ok'


if __name__ == '__main__':
    app.run()
