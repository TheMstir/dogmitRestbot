import telebot
import requests
import random
import time

bot = telebot.TeleBot("6025838180:AAFmaoqp7RpQpsrU45YOl0N0lH_6iCAzljo", parse_mode='HTML')


@bot.message_handler(regexp='Привет')
@bot.message_handler(commands=['hello-world'])
def hello_start(message):
    bot.send_message(message.chat.id, 'Привет, я бот!')

bot.polling(none_stop=True)
