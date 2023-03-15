import telebot
import requests
import random
import time

bot = telebot.TeleBot("6025838180:AAFmaoqp7RpQpsrU45YOl0N0lH_6iCAzljo", parse_mode='HTML')


@bot.message_handler(regexp='Привет')
@bot.message_handler(commands=['hello-world'])
def hello_start(message):
    bot.send_message(message.chat.id, 'Привет, я бот!')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    rand_m = random.randint(1, 2)
    if rand_m == 1:
        mess = f'Bau-Wau <b>{message.from_user.first_name}</b> я бот-Песмит!\n' \
               f'Поисковый пес (◕ᴥ◕ʋ) компании "Too Easy Travel"!' \
               f'Готов помогать в твоих поисках! '
    else:
        mess = f'Привет! <b>{message.from_user.first_name}</b> я поисковая собачка 🐕 компании "Too Easy Travel"!, ' \
               f'Я здесь специально для того, чтобы помочь тебе найти самую лучшую гостиницу для отдыха!'
    bot.send_message(message.chat.id, mess, parse_mode='HTML')
    time.sleep(1.5)
    bot.send_message(message.chat.id, 'Хочешь узнать как со мной работать? Жми /help,\n'
                                      'Если все знаешь то давай приступать\n'
                                      '/заглушка для будущих команд в виде меню/')


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, 'Список команд для работы: :: (•ᴥ• )́`́’́`́’⻍')


bot.polling(none_stop=True)
