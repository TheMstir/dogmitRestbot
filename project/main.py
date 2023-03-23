import datetime

import telebot
import random
import time
from weather import get_weather_box
import config
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot import types
from telebot import custom_filters
from hotels_hostels import get_hotels_box
import Homeland_rus
from history_controller import history_file
import requests
import urllib
from telebot.types import InputMediaPhoto
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

# @DogmeetRestbot
cash_storage = StateMemoryStorage()

bot = telebot.TeleBot(config.token, state_storage=cash_storage)


class MyStates(StatesGroup):
    """Хранлилище для промежуточных данных поискового запроса"""
    flag = State()  # в дальнейшем для определения сортировки
    city = State()  # название региона поиска
    count_place = State()  # количество предлагаемых отелей
    count_photos = State()  # None/5(max)
    come_in = State()
    come_out = State()



@bot.message_handler(regexp='Привет')
@bot.message_handler(commands=['hello-world'])
def hello_start(message: types.Message):
    """
    Бот здоровается несколькими вариантами в ответ на преветсвие
    """
    dice = random.randint(0, 4)
    mes = ''
    if dice == 0:
        mes = 'Готов к работе!'
    elif dice == 1:
        mes = 'Привет! Я бот искатель гостиниц! 👋'
    elif dice == 2:
        mes = 'Привет! 👋 У нас принято начинать с команды /start'
    elif dice == 3:
        mes = 'Это лишь тестовая версия, я обязательно всему научусь и помогу вам, но позже'
    elif dice == 4:
        mes = facts()

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
    time.sleep(1)
    bot.send_message(message.chat.id, f'Хочешь узнать как со мной работать? Жми /help,\n'
                                      f'Включить быстрое меню? /fast_menu\n'
                                      f'Если все знаешь то давай приступать\n')
    fact = facts()
    bot.send_message(message.chat.id, fact)


@bot.message_handler(commands=['fast_menu'])
def menu(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("👋 Быстрый поиск", "❓ Help/Menu")
    bot.send_message(message.from_user.id, 'ok', reply_markup=markup)


@bot.message_handler(commands=['help'])
def show_help_menu(message: types.Message):
    """
    Меню навигации в виде записи для помощи
    позволяет быстро перейти к основному функционалу
    иногда подкидывает факт из списка
    """
    mess = '''Гав! 🐶 Вот что мы можем сделать прямо сейчас:
/start чтобы начать наше общение
/low_price чтобы выбрать самые доступные по цене гостиницы ⛺🏚️
/high_price чтобы выбрать самые крутые и дорогие места для жизни 💎🏛️
/best_deal чтобы найти лучшие предложения в тех местах куда вы направляетесь 💼💰
/homeland_rus чтобы посмотреть гостиницы в городах России /для малых городов, только список/
/weather чтобы ознакомиться с погодой на местности и решиться на выбор поближе к пляжу🌅
/history БУДЕТ СПОСОБНО отправить вам вашу историю запросов
/cancel ❌ отменяет введенные данные и позволяет ввести новый запрос города ♻️
Можем просто немного пообщаться, но помни что я всего-лишь цифровой 🐕‍🦺 бот-песик и умею не так уж и много
    '''
    bot.send_message(message.chat.id, mess, parse_mode='HTML')
    dice = random.randint(1, 6)
    if dice == 6:
        time.sleep(0.5)
        bot.send_message(message.chat.id, facts())


@bot.message_handler(commands=['homeland_rus'])
def homelandrus(message: types.Message):
    """Функция поиска отелей в регионе
    где нет gaiaId, соответственно без сортировки, просто выдачей
    """
    bot.send_message(message.chat.id, 'Поищем местные отели:  ️🈂️')
    time.sleep(1)
    sent = bot.send_message(message.chat.id, 'В каком городе будем искать?: ')
    bot.register_next_step_handler(sent, homeland)


@bot.message_handler(commands=['low_price'])
def low_price(message: types.Message):
    """Функция поиска отелей с самой низкой ценой
    выставляет флаг поиска по 'PRICE_LOW_TO_HIGH'
    ведет к цепочке стандартного сбора информации
    """
    bot.send_message(message.chat.id, 'Поищем дешевые отели:  ️🈂️')
    bot.set_state(message.from_user.id, MyStates.flag, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['flag'] = 'PRICE_LOW_TO_HIGH'
    time.sleep(1)
    bot.send_message(message.chat.id, 'В каком городе будем искать?: ')

    bot.set_state(message.from_user.id, MyStates.city, message.chat.id)


@bot.message_handler(commands=['high_price'])
def high_price(message: types.Message):
    """Функция поиска отелей с самой высокой ценой.
    На данный момент предельная цена ограничена 200 долларами, но в дальнейшем можно сделать
    параметр настраиваемым
    выставляет флаг поиска 'PRICE_HIGHEST_FIRST'
    ведет к цепочке стандартного сбора информации
    """
    bot.send_message(message.chat.id, 'Будем искать лучшие предложения: 💸️🧐')

    bot.set_state(message.from_user.id, MyStates.flag, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['flag'] = 'PRICE_HIGHEST_FIRST'
    time.sleep(0.2)
    bot.send_message(message.chat.id, 'Буду стараться🐕! В каком городе ищем?: ')

    bot.set_state(message.from_user.id, MyStates.city, message.chat.id)


@bot.message_handler(commands=['best_deal'])
def best_price(message: types.Message):
    """Функция поиска отелей с самым лучшим соотношением в библиотеке
    судя по всему соотносит параметры скидок и расстояния от центра
    выставляет флаги 'STANCE_FROM_LANDMARK', 'BEST_SELLER'
    на данный момент от нее и идет сборка необходимых данных
    """
    bot.send_message(message.chat.id, 'Конечно помогу в поиске лучших предложений, товарищ!🦮:  ️🉐')

    bot.set_state(message.from_user.id, MyStates.flag, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['flag'] = 'STANCE_FROM_LANDMARK', 'BEST_SELLER'
    time.sleep(1)
    bot.send_message(message.chat.id, 'В каком городе собираемся заночевать?🏖️: ')

    bot.set_state(message.from_user.id, MyStates.city, message.chat.id)


@bot.message_handler(state=MyStates.city)
def get_city_seartch(message: types.Message):
    """
    Запрашивается в случае получения названия города запроса
    присваивает название города для дальнейшего применения
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text
    bot.send_message(message.chat.id, 'Классный город!🦮 Давайте посмотрим...')
    date_start(message)

@bot.message_handler(state=MyStates.come_in)  # вызов по команде для тестирования
def date_start(message: types.Message):
    """
    Запуск мини календаря для выбора даты
    """
    calendar, step = DetailedTelegramCalendar(calendar_id=0,
                                              min_date=datetime.date.today(),
                                              locale='ru').build()
    bot.send_message(message.chat.id, 'Когда планируете заезжать?', reply_markup=calendar)


def date_out(message: types.Message):
    """
    Запуск сбора даты выезда
    """
    chat_id = message.chat.id
    user_id = message.chat.id

    with bot.retrieve_data(user_id, chat_id) as data:
        date_in = data.get('come_in', datetime.date.today)

    calendar, step = DetailedTelegramCalendar(calendar_id=1,
                                              min_date=date_in + datetime.timedelta(days=1),
                                              locale='ru').build()
    bot.send_message(message.chat.id, 'Отлично! А когда будете выезжать', reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=0))
def date_in_calendar(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.message.chat.id

    result, key, step = DetailedTelegramCalendar(calendar_id=0,
                                                 min_date=datetime.date.today(),
                                                 locale='ru').process(callback_query.data)
    if not result and key:
        bot.edit_message_text('Когда планируете заезжать?',
                              chat_id,
                              callback_query.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(user_id, chat_id) as state_data:
            state_data['come_in'] = result

        bot.edit_message_text(f'Дата въезда {result}',
                              chat_id,
                              callback_query.message.message_id)
        date_out(callback_query.message)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def date_out_calendar(callback_query: types.CallbackQuery):
    """
    Календарь позволяет выбрать дату вы быстром меню
    после чего даты заезда и выезда передаются в переменные
    """
    chat_id = callback_query.message.chat.id
    user_id = callback_query.message.chat.id
    with bot.retrieve_data(user_id, chat_id) as data:
        date_in = data.get('come_in', datetime.date.today)

    result, key, step = DetailedTelegramCalendar(calendar_id=1,
                                                 min_date=date_in + datetime.timedelta(days=1),
                                                 locale='ru').process(callback_query.data)
    if not result and key:
        bot.edit_message_text('Отлично! А когда будете выезжать',
                              chat_id,
                              callback_query.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(user_id, chat_id) as data:
            data['come_out'] = result

        bot.edit_message_text(f'Дата выезда {result}',
                              chat_id,
                              callback_query.message.message_id)

        bot.set_state(user_id, MyStates.count_place, chat_id)
        bot.send_message(chat_id, 'Мне нравится🌭🐶! Сколько гостиниц хочешь посмотреть?')


@bot.message_handler(state=MyStates.count_place, is_digit=True)
def get_count_place(message: types.Message) -> None:
    """
    Получает количество отелей для вывода
    пока ограничу 5 как максимум.
    """

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_place'] = message.text

    if data['count_place'].isdigit():
        data['count_place'] = int(data['count_place'])
        if data['count_place'] > 5:
            bot.send_message(message.chat.id, 'Я думаю 5 будет достаточно, 🐾 лапки коротковаты, я же маленький пес')
            data['count_place'] = 5
        markup_inline = types.InlineKeyboardMarkup()
        item_yes = types.InlineKeyboardButton(text='👋 ДА', callback_data='yes')
        item_no = types.InlineKeyboardButton(text='🚫 НЕТ', callback_data='no')

        markup_inline.add(item_yes, item_no)
        bot.send_message(message.chat.id, f'Гав! Отлично {message.from_user.first_name}! '
                                          f'показать фотографии?', reply_markup=markup_inline)

    else:
        bot.register_next_step_handler(message, incorrect)


@bot.callback_query_handler(func=lambda call: True)
def photos_yn(call: types.CallbackQuery) -> None:
    """
    Опрашивающие кнопки уточняют нужны ли фотографии отелей
    если нет, то пользователю сразу отправляется ответ.
    Предполагаю сдвинуть ответ в отдельную функцию, однако на данном этапе в этом нет
    необходимости
    """
    if call.data == 'yes':
        send = bot.send_message(call.message.chat.id, 'Отлично U・ᴥ・U! сколько хочешь фотографий, я сбегаю за ними!')
        bot.register_next_step_handler(send, photos_get)

    elif call.data == 'no':
        # просто передает ноль
        sent = bot.send_message(call.message.chat.id, 'Отлично!🐾 сейчас подготовлю ссылки')
        time.sleep(1)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['count_photos'] = 0
        bot.register_next_step_handler(sent, ready)
        bot.send_message(call.message.chat.id, 'Я 🐶подготовил! Высылать? 🦊 /go')

    else:
        incorrect()


@bot.message_handler(state=MyStates.count_photos, is_digit=True)
def photos_get(message: types.Message) -> None:
    """
    Запрашивается необходимость фотографий
    и выводиться финальный результат обработки
    Фотографии приходят дополнительным элементом списка и вынимаются из него в виде доп. сообщений
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photos'] = message.text
    if data['count_photos'].isdigit():
        if int(data['count_photos']) > 7:
            bot.send_message(message.chat.id, 'Много, я маленький, максимум 7 штук принесу')
            data['count_photos'] = 4
        elif int(data['count_photos']) == 1:
            bot.send_message(message.chat.id, 'Маловато, давай 2')
            data['count_photos'] = 2
        data['count_photos'] = int(data['count_photos'])
        sent = bot.send_message(message.chat.id, 'Отлично! сейчас подготовлю ссылки')
        time.sleep(0.5)
        bot.send_message(message.chat.id, '🐶Гавтовы!🦊 Высылать? /go')
        bot.register_next_step_handler(sent, ready)

    else:
        bot.register_next_step_handler(message, incorrect)


def ready(message: types.Message) -> None:
    """
    Функция завершающая сбор данных, отправляющая запарос в функцию поиска отелей
    собирает информацию в список 2х вариантов и в зависимости от значения фото выдает
    результаты двух видов.

    """
    datas = cash_storage.get_data(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, 'Пожалуйста, подождите, сейчас выдам.⏱')

    mess = get_hotels_box(datas['city'], datas['count_place'], datas['count_photos'], datas['flag'], datas['come_in'],
                          datas['come_out'])

    name_id = f'{message.from_user.first_name}_{message.from_user.last_name}'
    history_file(name_id, datas['city'], datas['count_place'], datas['flag'], mess)

    try:
        if datas['count_photos'] > 0:
            # докидываю сюда сообщения
            bot.send_message(message.chat.id, mess[0], parse_mode='HTML')

            for el in mess[1:]:
                el[0] = str(el[0])
                media_group = [types.InputTextMessageContent(el[0])]
                for elo in el[1]:
                    media_group.append(types.InputMediaPhoto(elo, el[0]))
                bot.send_media_group(chat_id=message.chat.id, media=media_group)

        else:
            for el in mess:
                bot.send_message(message.chat.id, *el, parse_mode='HTML')

    except:
        bot.send_message(message.chat.id, 'ГАВ!🐦📛 Сейчас фотографий нет, все лапки стер и не нашел',
                         parse_mode='HTML')

    weather = get_weather_box(datas['city'])  # добавление погоды на текущий момент в
    # городе где производиться поиск
    bot.send_message(message.chat.id, weather, parse_mode='HTML')
    # и удаляем мусор дичь
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state="*", commands=['cancel'])
def any_state(message: types.Message) -> None:
    """
    Сброс данных в States по запросу пользователя
    """
    data = cash_storage.get_data(message.from_user.id, message.chat.id)
    data['city'] = ''
    data['count_place'] = 0
    data['count_photos'] = 0
    data['come_in'] = None
    data['come_out'] = None

    bot.send_message(message.chat.id, "Ваши установки отменены.")
    bot.delete_state(message.from_user.id, message.chat.id)
    show_help_menu(message)


def homeland(message: types.Message) -> None:
    bot.set_state(message.from_user.id, '')
    city = message.text
    bot.send_message(message.chat.id, 'Хорошее место!🦮 сбегаю и посмотрю что там есть')
    mess = Homeland_rus.get_hotels(city)
    name_id = f'{message.from_user.first_name}_{message.from_user.last_name}'
    history_file(name_id, city, 0, 'местные', mess)
    for el in mess:
        bot.send_message(message.chat.id, el, parse_mode='HTML')

    weather = get_weather_box(city)
    bot.send_message(message.chat.id, weather, parse_mode='HTML')


@bot.message_handler(state=MyStates.count_place or MyStates.count_photos, is_digit=False)  # неверный числовой ввод
def incorrect(message: types.Message) -> None:
    """
    Неправильный вид данных для числового запроса перекидывает к старту
    """
    bot.send_message(message.chat.id, 'Гав, выглядит так, будто ты вводишь числа буквами... Я не знаю, '
                                      'просто введи число или лучше начнем сначала\n/help, /start')
    send_welcome(message)


@bot.message_handler(commands=['history'])
def histors(message: types.Message) -> None:
    """
    Функция показывает историю из ограниченного количества элементов
    затем высылает пользователю фаил с историей его запросов
    """
    name_id = f'{message.from_user.first_name}_{message.from_user.last_name}'

    try:
        with open(f'historys/{name_id}.txt', 'r', encoding='utf-8') as r:
            for i in range(15):
                fp = r.readline()
                fp = fp.partition('🏬')[0]
                fp = fp.replace('\\n', ' ').replace('[', '').replace("'", '')
                bot.send_message(message.from_user.id, fp, parse_mode='HTML')
            r.close()

        # отправка открытого файла с историей. Верстка там html но как лог подойдет
        with open(f'historys/{name_id}.txt', 'r', encoding='utf-8') as r:
            bot.send_document(message.chat.id, r)

    except:
        bot.send_message(message.from_user.id, 'Вууф... почему-то не могу найти продолжение твоей истории...')


@bot.message_handler(commands=['weather'])
def get_weather(message: types.Message) -> None:
    """
    Небольшая отсебятина выводящая погоду, так же по
     передает данные дополнительным сообщением к поиску гостиниц
    """
    sent = bot.send_message(message.chat.id, '🌆🧳Введите город: ', parse_mode='HTML')  #
    bot.register_next_step_handler(sent, weather_date)


def weather_date(message: types.Message) -> None:
    """
    Принимает запрос на погоду в каком-то городе
    Отправляет название в функцию и возвращает в бота соответсвующее сообщение
    """
    city = message.text
    mess = get_weather_box(city)
    bot.send_message(message.chat.id, mess, parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def date_from_user(message: types.Message) -> None:
    """
    Функция получает данные от пользователя и в случае необходимого запроса возвращает в переменную
    :return:
    """
    if message.text == '👋 Быстрый поиск':
        best_price(message)
    if message.text == '❓ Help/Menu':
        show_help_menu(message)


def facts() -> str:
    """
    Берет из приложенного файла со случайными фактами и возвращает ее.
    :return: строчку с фактом
    """
    with open('facts.txt', 'r', encoding='utf-8') as f:
        mess = f.read().split('\n')
        dice = random.randint(1, 10)
        fact = mess[dice]
    return fact


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

bot.infinity_polling(skip_pending=True)
