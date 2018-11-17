import logging

from flask import Flask, request

app = Flask(__name__)

# Логируем все что у нас есть в gunicorn, чтобы было видно в консоли
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    # Учитываем уровень логов самого gunicorn
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/telegram-handler', methods=['POST'])
def telegram():
    app.logger.info('Telegram updates: {}'.format(request.get_json().__repr__()))
    return 'Ok'


if __name__ == '__main__':
    app.run()
