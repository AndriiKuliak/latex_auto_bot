import os

import flask
import telebot

import config
from logger import logger
from security import GoogleCloudSecurityProxy

BOT_API_TOKEN = GoogleCloudSecurityProxy().get_bot_auth_token()

WEBHOOK_URL_PATH = "/%s/" % (BOT_API_TOKEN)

app = flask.Flask(__name__)
bot = telebot.TeleBot(BOT_API_TOKEN)

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'Hello'

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                    ("Hello, I am LaTeX Auto Bot.\n"
                     "For now I can onlu echo yor messages, but I promise to be smarter."))

@bot.message_handler(content_types=['text'])
def echo_message(message):
    bot.send_message(message.chat.id, message.text)

bot.remove_webhook()
bot.set_webhook(url=config.WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

if __name__ == "__main__":
    logger.info('Starting web server on port %s' % config.WEBHOOK_PORT)
    app.run(host=config.WEBHOOK_LISTEN,
            port=config.WEBHOOK_PORT,
            debug=True)
