from logging import debug

from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/telegram-handler')
def telegram():
    debug('Telegram updates: {}'.format(request.get_json().__repr__()))
    return 'Ok'


if __name__ == '__main__':
    app.run()
