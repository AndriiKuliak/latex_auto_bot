import os

import flask
import telebot

import config
from database_proxy import DBProxy
from logger import logger
from user_info import UserInfo, States
from security import GoogleCloudSecurityProxy
from latex_utilities import LatexUtilties

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
    bot.send_message(message.chat.id, "Just send a content of LaTeX document and receive back compiled PDF")


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
    bot.send_message(message.chat.id, "Just send a content of LaTeX document and receive back previews")


@bot.message_handler(commands=['help'])
def help_handler(message):
    user = db_proxy.get_user_info(UserInfo(message.from_user.id, States.START, message.date))

    if check_message_duplicate(user, message) == False:
        logger.warning("Message duplicate detected from user %d" % message.from_user.id)
        return

    user.last_message_time = message.date
    db_proxy.set_user_info(user)

    help_text = """This bot allows you to convert your raw LaTeX document to readable formats\n\n
                The following commands are currently supported:\n
                /convertlatex - This mode allows you convert LaTeX document to PDF\n
                /previewlatex - This mode allows you preview your LaTeX document\n\n
                LaTeX document should be send as message\n\n
                Enjoy!\n
                """

    bot.send_message(message.chat.id, help_text)


@bot.message_handler(content_types=['text'])
def regular_text_handler(message):
    user = db_proxy.get_user_info(UserInfo(message.from_user.id, States.START, message.date))

    if check_message_duplicate(user, message) == False:
        logger.warning("Message duplicate detected from user %d" % message.from_user.id)
        return

    user.last_message_time = message.date
    db_proxy.set_user_info(user)

    logger.debug("Current user state: %s" % str(user))

    if user.last_state == States.CONVERT_DOCUMENT:
        try:
            logger.info("Generating PDF for user {}".format(user.user_id))

            bot.send_message(message.chat.id, "Let's generate PDF for you ;)")
            path_to_doc = LatexUtilties().generate_pdf(user.user_id, message.text)

            with open(path_to_doc, "rb") as doc:
                bot.send_document(message.chat.id, doc, caption="Here you go")
            
            os.unlink(path_to_doc)

        except Exception as e:
            logger.exception("An exception occured: {}".format(e))
            bot.send_message(message.chat.id, "Something went wrong! Please check your document")

    elif user.last_state == States.PREVIEW_DOCUMENT:
        try:
            logger.info("Generating preview for user {}".format(user.user_id))

            bot.send_message(message.chat.id, "Let's render your document ;)")
            path_to_pictures = LatexUtilties().generate_png(user.user_id, message.text)

            media_group = [ telebot.types.InputMediaPhoto(open(doc, "rb")) for doc in path_to_pictures ]

            bot.send_media_group(message.chat.id, media_group)
            bot.send_message(message.chat.id, "Here you go")

            for picture in path_to_pictures:
                os.unlink(picture)

        except Exception as e:
            logger.exception("An exception occured: {}".format(e))
            bot.send_message(message.chat.id, "Something went wrong! Please check your document")

    elif user.last_state == States.CHECK_SYNTAX:
        bot.send_message(message.chat.id, "This function hasn't been implemented yet. \nBut, be patient.")
    else:
        bot.send_message(message.chat.id, "I don't have time for chat with you! Please tell me what to do.")

if __name__ == '__main__':
    logger.info('Starting web server {} on port {}'.format(config.WEBHOOK_LISTEN, config.WEBHOOK_PORT))
    app.run(host=config.WEBHOOK_LISTEN, port=config.WEBHOOK_PORT, debug=True)
