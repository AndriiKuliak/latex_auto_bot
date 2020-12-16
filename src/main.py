import telebot

bot_proxy = telebot.TeleBot('')

@bot_proxy.message_handler(commands=['start'])
def initiate_session(message):
    bot_proxy.send_message(message.chat.id, 'Hello, fellow!')

@bot_proxy.message_handler(content_types=['text'])
def handle_user_input(message):
    bot_proxy.send_message(message.chat.id, message.text)

bot_proxy.polling()
