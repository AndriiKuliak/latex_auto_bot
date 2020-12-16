import telebot
import logging

from security import GoogleCloudSecurityProxy

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s - %(message)s')

sec_manager_proxy = GoogleCloudSecurityProxy()

bot_proxy = telebot.TeleBot(sec_manager_proxy.get_bot_auth_token())

@bot_proxy.message_handler(commands=['start'])
def initiate_session(message):
    logging.debug("Handling session initialisation from %s(id: %d)", message.from_user.username, message.from_user.id)
    bot_proxy.send_message(message.chat.id, 'Hello, fellow!')

@bot_proxy.message_handler(content_types=['text'])
def handle_user_input(message):
    logging.debug("Handling user text input from %s(id: %d)", message.from_user.username, message.from_user.id)
    bot_proxy.send_message(message.chat.id, message.text)

if __name__ == "__main__":
    logging.info('Starting nessage polling from Telegram servers')
    bot_proxy.polling()
