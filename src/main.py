import os

import flask
import telebot

import config
from database_proxy import DBProxy
from logger import logger
from user_info import UserInfo, States
from security import GoogleCloudSecurityProxy

BOT_API_TOKEN = GoogleCloudSecurityProxy().get_bot_auth_token()
WEBHOOK_URL_PATH = "/%s/" % (BOT_API_TOKEN)

app = flask.Flask(__name__)
bot = telebot.TeleBot(BOT_API_TOKEN)
db_proxy = DBProxy()

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


bot.remove_webhook()
bot.set_webhook(url=config.WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

def check_message_duplicate(user, message):
    return States.START == user or message.date != user.last_message_time


@bot.message_handler(commands=['start'])
def handle_start(message):
    user = db_proxy.get_user_info(UserInfo(message.from_user.id, States.START, message.date))

    if check_message_duplicate(user, message) == False:
        logger.warning("Message duplicate detected from user %d" % message.from_user.id)
        return

    response = ""
    if user.last_state == States.START:
        response = ("Hello, I am LaTeX Auto Bot.\n\n"
                    "Let's play with LaTeX documents!")
        user.last_state = States.MAIN_MENU
    else:
        response = "You have already stared me!"

    db_proxy.set_user_info(user)

    bot.send_message(message.chat.id, response)


@bot.message_handler(commands=['checklatex'])
def handle_cheklatex(message):
    user = db_proxy.get_user_info(UserInfo(message.from_user.id, States.START, message.date))

    if check_message_duplicate(user, message) == False:
        logger.warning("Message duplicate detected from user %d" % message.from_user.id)
        return

    user.last_state = States.CHECK_SYNTAX
    user.last_message_time = message.date
    db_proxy.set_user_info(user)

    bot.send_message(message.chat.id, "This mode allows you to check document on errors")


@bot.message_handler(commands=['convertlatex'])
def handle_convertlatex(message):
    user = db_proxy.get_user_info(UserInfo(message.from_user.id, States.START, message.date))

    if check_message_duplicate(user, message) == False:
        logger.warning("Message duplicate detected from user %d" % message.from_user.id)
        return

    user.last_state = States.CONVERT_DOCUMENT
    user.last_message_time = message.date
    db_proxy.set_user_info(user)

    bot.send_message(message.chat.id, "This mode allows you convert LaTeX document to PDF")


@bot.message_handler(commands=['previewlatex'])
def handle_previewlatex(message):
    user = db_proxy.get_user_info(UserInfo(message.from_user.id, States.START, message.date))

    if check_message_duplicate(user, message) == False:
        logger.warning("Message duplicate detected from user %d" % message.from_user.id)
        return

    user.last_state = States.PREVIEW_DOCUMENT
    user.last_message_time = message.date
    db_proxy.set_user_info(user)

    bot.send_message(message.chat.id, "This mode allows you preview your LaTeX document")


@bot.message_handler(commands=['help'])
def help_handler(message):
    user = db_proxy.get_user_info(UserInfo(message.from_user.id, States.START, message.date))

    if check_message_duplicate(user, message) == False:
        logger.warning("Message duplicate detected from user %d" % message.from_user.id)
        return

    user.last_message_time = message.date
    db_proxy.set_user_info(user)

    bot.send_message(message.chat.id, "Help...")


@bot.message_handler(content_types=['text'])
def regular_text_handler(message):
    user = db_proxy.get_user_info(UserInfo(message.from_user.id, States.START, message.date))

    if check_message_duplicate(user, message) == False:
        logger.warning("Message duplicate detected from user %d" % message.from_user.id)
        return

    user.last_message_time = message.date
    db_proxy.set_user_info(user)

    bot.send_message(message.chat.id, "Current user state: {}".format(str(user)))


if __name__ == '__main__':
    logger.info('Starting web server {} on port {}'.format(config.WEBHOOK_LISTEN, config.WEBHOOK_PORT))
    app.run(host=config.WEBHOOK_LISTEN, port=config.WEBHOOK_PORT, debug=True)
