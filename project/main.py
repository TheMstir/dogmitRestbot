import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
import random
import time
from weather import get_weather_box
import logging
import config
import sqlite3
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot import types
from hotels_hostels import get_hotels_box


# @DogmeetRestbot
cash_storage = StateMemoryStorage()

bot = telebot.TeleBot(config.token, parse_mode='HTML', state_storage=cash_storage)

# пара быстрых кнопок потом переедет в функцию
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("👋 Быстрый поиск")
btn2 = types.KeyboardButton("❓ Help/Menu")
markup.add(btn1, btn2)


class MyStates(StatesGroup):
    """Хранлилище для промежуточных данных поискового запроса"""
    flag = State() # в дальнейшем для определения
    city = State()
    count_place = State()
    count_photos = State()  # None/10(max)


@bot.message_handler(regexp='Привет')
@bot.message_handler(commands=['hello-world'])
def hello_start(message: types.Message):
    """
    Бот здоровается несколькими вариантами в ответ на преветсвие
    """
    dice = random.randint(0, 2)
    if dice == 0:
        mes = 'Готов к работе!'
    elif dice == 1:
        mes = 'Привет! Я бот искатель гостиниц! 👋'
    elif dice == 2:
        mes = 'Привет! 👋 У нас принято начинать с команды /start'
    else:
        mes = 'Это лишь тестовая версия, я обязательно всему научусь и помогу вам, но позже'

# придумать как анализировать постоянный запрос и выдавать смешные цитаты из API
    bot.send_message(message.chat.id, mes, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    rand_m = random.randint(1, 2)
    if rand_m == 1:
        mess = f'Bau-Wau <b>{message.from_user.first_name}</b> я бот-Песмит!\n' \
               f'Поисковый пес (◕ᴥ◕ʋ) компании "Too Easy Travel"!\n' \
               f'Готов помогать в твоих поисках! '
    else:
        mess = f'Привет! <b>{message.from_user.first_name}</b> я поисковая собачка 🐕 компании "Too Easy Travel"!, ' \
               f'Я здесь специально для того, чтобы помочь тебе найти самую лучшую гостиницу для отдыха!'
    bot.send_message(message.chat.id, mess, parse_mode='HTML')
    time.sleep(1.5)
    # TODO прикрутить счетчик предложений помощи/фактов, чтобы не надоедать
    bot.send_message(message.chat.id, 'Хочешь узнать как со мной работать? Жми /help,\n'
                                      'Если все знаешь то давай приступать\n'
                                      '/заглушка для будущих команд в виде меню или интересного факта о путешествиях/')


@bot.message_handler(commands=['help'])
def show_help_menu(message: types.Message):
    """
    Меню навигации в виде записи для помощи
    позволяет быстро перейти к основному функционалу
    """
    mess = '''Гав! 🐶 Вот что мы можем сделать прямо сейчас:
/start чтобы начать наше общение
/low_price чтобы выбрать самые доступные по цене гостиницы ⛺🏚️
/high_price чтобы выбрать самые крутые и дорогие места для жизни 💎🏛️
/best_deal чтобы найти лучшие предложения в тех местах куда вы направляетесь 💼💰
/homeland_rus чтобы посмотреть гостиницы в городах России /для малых городов/
/weather чтобы ознакомиться с погодой на местности и решиться на выбор поближе к пляжу🌅
/history БУДЕТ СПОСОБНО отправить вам вашу историю запросов
/cancel 🗙 отменяет введенные данные и позволяет ввести новый запрос города ♺
Можем просто немного пообщаться, но помни что я всего-лишь цифровой 🐕‍🦺 бот-песик и умею не так уж и много
    '''
    bot.send_message(message.chat.id, mess, parse_mode='HTML')


@bot.message_handler(commands=['low_price'])
def low_price(message: types.Message):
    """Функция поиска отелей с самой низкой ценой
    выставляет флаг поиска по 'PRICE_LOW_TO_HIGH'
    ведет к цепочке стандартного сбора информации
    """
    bot.send_message(message.chat.id, 'Поищем дешевые отели:  ️🈂️')
    MyStates.flag = 'PRICE_LOW_TO_HIGH'
    time.sleep(1)
    sent = bot.send_message(message.chat.id, 'В каком городе будем искать?: ')
    bot.register_next_step_handler(sent, get_city_seartch)

@bot.message_handler(commands=['high_price'])
def high_price(message: types.Message):
    """Функция поиска отелей с самой высокой ценой.
    На данный момент предельная цена ограничена 200 долларами, но в дальнейшем можно сделать
    параметр настраиваемым
    выставляет флаг поиска 'PRICE_HIGHEST_FIRST'
    ведет к цепочке стандартного сбора информации
    """
    bot.send_message(message.chat.id, 'Будем искать лучшие предложения: 💸️🧐')
    MyStates.flag = 'PRICE_HIGHEST_FIRST'
    time.sleep(0.2)
    sent = bot.send_message(message.chat.id, 'Буду стараться🐕! В каком городе ищем?: ')
    bot.register_next_step_handler(sent, get_city_seartch)


@bot.message_handler(commands=['best_deal'])
def best_price(message: types.Message):
    """Функция поиска отелей с самым лучшим соотношением в библиотеке
    судя по всему соотносит параметры скидок и расстояния от центра
    выставляет флаги 'STANCE_FROM_LANDMARK', 'BEST_SELLER'
    на данный момент от нее и идет сборка необходимых данных
    """
    bot.send_message(message.chat.id, 'Конечно помогу в поиске лучших предложений, товарищ!🦮:  ️🉐')
    MyStates.flag = 'STANCE_FROM_LANDMARK', 'BEST_SELLER'
    time.sleep(1)
    sent = bot.send_message(message.chat.id, 'В каком городе собираемся заночевать?🏖️: ')
    bot.register_next_step_handler(sent, get_city_seartch)


def get_city_seartch(message: types.Message):
    """
    Запрашивается в случае получения названия города запроса
    присваивает название города для дальнейшего применения
    """
    bot.set_state(message.from_user.id, '')
    MyStates.city = message.text
    print(MyStates.city)
    sent = bot.send_message(message.chat.id, 'Классный город!🦮 Сколько гостиниц хочешь посмотреть?')
    bot.register_next_step_handler(sent, get_count_place)


def get_count_place(message: types.Message):
    """
    Получает количество отелей для вывода
    пока ограничу 5 как максимум.
    """
    bot.set_state(message.from_user.id, '')
    count = message.text
    if count.isdigit():
        MyStates.count_place = int(count)
        if MyStates.count_place > 5:
            bot.send_message(message.chat.id, 'Я думаю 5 будет достаточно, 🐾 лапки коротковаты, я же маленький пес')
            MyStates.count_place = 5
        print(MyStates.count_place)
        markup_inline = types.InlineKeyboardMarkup()
        item_yes = types.InlineKeyboardButton(text='👋 ДА', callback_data='yes')
        item_no = types.InlineKeyboardButton(text='🚫 НЕТ', callback_data='no')

        markup_inline.add(item_yes, item_no)
        print(message.chat.id)
        bot.send_message(message.chat.id, f'Гав! Отлично {message.from_user.first_name}!'
                                          f'показать фотографии?', reply_markup=markup_inline)

    else:
        bot.register_next_step_handler(message, incorrect)


@bot.callback_query_handler(func=lambda call: True)
def photos_yn(call):
    print(call.message.chat.id)
    if call.data == 'yes':
        sent = bot.send_message(call.message.chat.id, 'Отлично, сколько хочешь фотографий, я сбегаю за ними!')
        bot.register_next_step_handler(sent, photos_get)
    elif call.data == 'no':
        # переделать чтобы просто получать ноль
        bot.send_message(call.message.chat.id, 'Отлично!🐾 сейчас подготовлю ссылки')
        time.sleep(1)
        mess = get_hotels_box(MyStates.city, MyStates.count_place, 0, MyStates.flag)
        print(mess)

        # get_hotels() # Ссылка на функцию low_price_s в hotel_hostels
        for el in mess:
            bot.send_message(call.message.chat.id, *el, parse_mode='HTML')

        weather = get_weather_box(MyStates.city)  # добавление погоды на текущий момент в
        # городе где производиться поиск
        bot.send_message(call.message.chat.id, weather, parse_mode='HTML')
    else:
        bot.register_next_step_handler(call.message.chat.id, incorrect)


def photos_get(message: types.Message):
    """
    Запрашивается необходимость фотографий
    """
    bot.set_state(message.from_user.id, '')
    count = message.text
    if count.isdigit():
        MyStates.count_photos = int(count)
        bot.send_message(message.chat.id, 'Отлично! сейчас подготовлю ссылки')
        time.sleep(0.5)
        mess = get_hotels_box(MyStates.city, MyStates.count_place, MyStates.count_photos, MyStates.flag)

        for el in mess:
            bot.send_message(message.chat.id, el[1], parse_mode='HTML')
            for elo in el[2]:
                photo = open(f'{elo}', 'rb')
                bot.send_photo(message.chat.id, photo)

        weather = get_weather_box(MyStates.city)  # добавление погоды на текущий момент в
        # городе где производиться поиск
        bot.send_message(message.chat.id, weather, parse_mode='HTML')
    else:
        bot.register_next_step_handler(message, incorrect)


@bot.message_handler(state="*", commands=['cancel'])
def any_state(message: types.Message):
    """
    Сброс данных в States по запросу пользователя
    """
    bot.send_message(message.chat.id, "Ваши установки отменены.")
    MyStates.city = ''
    MyStates.count_place = 0
    MyStates.count_photos = 0
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=MyStates.count_place or MyStates.count_photos, is_digit=False)  # неверный числовой ввод
def incorrect(message: types.Message):
    """
    Неправильный вид данных для числового запроса
    """
    bot.send_message(message.chat.id, 'Гав, выглядит так, будто ты вводишь числа буквами... Я не знаю, '
                                      'просто введи число или лучше начнем сначала /help, /start')
    bot.register_next_step_handler(message, send_welcome)


@bot.message_handler(commands=['weather'])
def get_weather(message: types.Message):
    """
    Небольшая отсебятина выводящая погоду, так же по
    необходимости БУДЕТ передаВАТЬ данные ДОПОЛНИТЕЛЬНЫМ СООБЩЕНИЕМ к поиску гостиниц
    """
    sent = bot.send_message(message.chat.id, '🌆🧳Введите город: ', parse_mode='HTML')  #
    bot.register_next_step_handler(sent, weather_date)


def weather_date(message: types.Message):
    city = message.text
    print(city)
    mess = get_weather_box(city)
    bot.send_message(message.chat.id, mess, parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def date_from_user(message: types.Message):
    """
    Функция получает данные от пользователя и в случае необходимого запроса возвращает в переменную
    :return:
    """
    return message.text



#bot.enable_save_next_step_handlers(delay=2)
#bot.load_next_step_handlers()

bot.polling(none_stop=True)


#  logger = telebot.logger
#  telebot.logger.setLevel(logging.DEBUG)
