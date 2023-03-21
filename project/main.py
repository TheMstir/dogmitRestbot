import telebot
import random
import time
from weather import get_weather_box
import requests
import logging
import config
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot import types
from telebot import custom_filters
from hotels_hostels import get_hotels_box
import Homeland_rus
from history_controller import history_file

# @DogmeetRestbot
cash_storage = StateMemoryStorage()

bot = telebot.TeleBot(config.token, state_storage=cash_storage)


class MyStates(StatesGroup):
    """Хранлилище для промежуточных данных поискового запроса"""
    flag = State()  # в дальнейшем для определения сортировки
    city = State()  # название региона поиска
    count_place = State()  # количество предлагаемых отелей
    count_photos = State()  # None/5(max)

@bot.message_handler(regexp='Привет')
@bot.message_handler(commands=['hello-world'])
def hello_start(message: types.Message):
    """
    Бот здоровается несколькими вариантами в ответ на преветсвие
    """
    dice = random.randint(0, 3)
    if dice == 0:
        mes = 'Готов к работе!'
    elif dice == 1:
        mes = 'Привет! Я бот искатель гостиниц! 👋'
    elif dice == 2:
        mes = 'Привет! 👋 У нас принято начинать с команды /start'
    elif dice == 3:
        mes = 'Это лишь тестовая версия, я обязательно всему научусь и помогу вам, но позже'
    else:
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
    # пара быстрых кнопок потом переедет в функцию


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
/cancel 🗙 отменяет введенные данные и позволяет ввести новый запрос города ♺
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

    #bot.register_next_step_handler(sent, get_city_seartch)


@bot.message_handler(state=MyStates.city)
def get_city_seartch(message: types.Message):
    """
    Запрашивается в случае получения названия города запроса
    присваивает название города для дальнейшего применения
    """
    bot.send_message(message.chat.id, 'Классный город!🦮 Сколько гостиниц хочешь посмотреть?')

    bot.set_state(message.from_user.id, MyStates.count_place, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text


@bot.message_handler(state=MyStates.count_place, is_digit=True)
def get_count_place(message: types.Message):
    """
    Получает количество отелей для вывода
    пока ограничу 5 как максимум.
    """
    print(message.from_user.id, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_place'] = message.text
        print(data['count_place'])

    if data['count_place'].isdigit():
        data['count_place'] = int(data['count_place'])
        if data['count_place'] > 5:
            bot.send_message(message.chat.id, 'Я думаю 5 будет достаточно, 🐾 лапки коротковаты, я же маленький пес')
            data['count_place'] = 5
        markup_inline = types.InlineKeyboardMarkup()
        item_yes = types.InlineKeyboardButton(text='👋 ДА', callback_data='yes')
        item_no = types.InlineKeyboardButton(text='🚫 НЕТ', callback_data='no')

        markup_inline.add(item_yes, item_no)
        print(message.chat.id)
        bot.send_message(message.chat.id, f'Гав! Отлично {message.from_user.first_name}! '
                                          f'показать фотографии?', reply_markup=markup_inline)

    else:
        bot.register_next_step_handler(message, incorrect)


@bot.callback_query_handler(func=lambda call: True)
def photos_yn(call):
    """
    Опрашивающие кнопки уточняют нужны ли фотографии отелей
    если нет, то пользователю сразу отправляется ответ.
    Предполагаю сдвинуть ответ в отдельную функцию, однако на данном этапе в этом нет
    необходимости
    """
    print(call.from_user.id, call.message.chat.id)
    if call.data == 'yes':
        send = bot.send_message(call.message.chat.id, 'Отлично U・ᴥ・U! сколько хочешь фотографий, я сбегаю за ними!')
        bot.register_next_step_handler(send, photos_get)

    elif call.data == 'no':
        # переделать чтобы просто получать ноль

        sent = bot.send_message(call.message.chat.id, 'Отлично!🐾 сейчас подготовлю ссылки')
        time.sleep(1)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['count_photos'] = 0

        print(call.from_user.id, call.message.chat.id)
        bot.register_next_step_handler(sent, ready)
        bot.send_message(call.message.chat.id, 'Я 🐶подготовил! Высылать? 🦊 /go')

    else:
        bot.register_next_step_handler(call.message.chat.id, incorrect)


@bot.message_handler(state=MyStates.count_photos, is_digit=True)
def photos_get(message: types.Message):
    """
    Запрашивается необходимость фотографий
    и выводиться финальный результат обработки
    Фотографии приходят дополнительным элементом списка и вынимаются из него в виде доп. сообщений
    """
    print('начали считать')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photos'] = message.text
    if data['count_photos'].isdigit():
        if int(data['count_photos']) > 5:
            bot.send_message(message.chat.id, 'Много, я маленький, максимум 5 штук принесу')
            data['count_photos'] = 4
        data['count_photos'] = int(data['count_photos'])
        sent = bot.send_message(message.chat.id, 'Отлично! сейчас подготовлю ссылки')
        time.sleep(0.5)
        bot.send_message(message.chat.id, '🐶Гавтовы!🦊 Высылать? /go')
        bot.register_next_step_handler(sent, ready)

    else:
        bot.register_next_step_handler(message, incorrect)

    print('count_p прошел')
    print(message.from_user.id, message.chat.id)


def ready(message: types.Message):
    """
    Функция завершающая сбор данных, отправляющая запарос в функцию поиска отелей
    собирает информацию в список 2х вариантов и в зависимости от значения фото выдает
    результаты двух видов.

    """
    print('кто-то пришел')
    data = cash_storage.get_data(message.from_user.id, message.chat.id)

    mess = get_hotels_box(data['city'], data['count_place'], data['count_photos'], data['flag'])

    name_id = f'{message.from_user.first_name}_{message.from_user.last_name}'
    history_file(name_id, data['city'], data['count_place'], data['flag'], mess)

    try:
        if data['count_photos'] > 0:
            bot.send_message(message.chat.id, mess[0], parse_mode='HTML')
            for el in mess[1:]:
                print(el)
                bot.send_message(message.chat.id, el[0], parse_mode='HTML')
                for elo in el[1]:
                    print(elo)
                    bot.send_photo(message.chat.id, elo)
        else:
            for el in mess:
                bot.send_message(message.chat.id, *el, parse_mode='HTML')

    except:
        bot.send_message(message.chat.id, 'ГАВ!🐦📛 Сейчас фотографий нет, все лапки стер и не нашел',
                         parse_mode='HTML')

    weather = get_weather_box(data['city'])  # добавление погоды на текущий момент в
    # городе где производиться поиск
    bot.send_message(message.chat.id, weather, parse_mode='HTML')
    # и удаляем мусор дичь
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state="*", commands=['cancel'])
def any_state(message: types.Message):
    """
    Сброс данных в States по запросу пользователя
    """
    data = cash_storage.get_data(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Ваши установки отменены.")

    data['city'] = ''
    data['count_place'] = 0
    data['count_photos'] = 0
    # видимо то что выше не нужно.
    bot.delete_state(message.from_user.id, message.chat.id)
    show_help_menu(message)


def homeland(message):
    bot.set_state(message.from_user.id, '')
    city = message.text
    print(city)
    bot.send_message(message.chat.id, 'Хорошее место!🦮 сбегаю и посмотрю что там есть')
    mess = Homeland_rus.get_hotels(city)
    for el in mess:
        bot.send_message(message.chat.id, el, parse_mode='HTML')

    weather = get_weather_box(city)
    bot.send_message(message.chat.id, weather, parse_mode='HTML')


@bot.message_handler(state=MyStates.count_place or MyStates.count_photos, is_digit=False)  # неверный числовой ввод
def incorrect(message: types.Message):
    """
    Неправильный вид данных для числового запроса
    """
    bot.send_message(message.chat.id, 'Гав, выглядит так, будто ты вводишь числа буквами... Я не знаю, '
                                      'просто введи число или лучше начнем сначала\n/help, /start')
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
    """
    Принимает запрос на погоду в каком-то городе
    Отправляет название в функцию и возвращает в бота соответсвующее сообщение
    """
    city = message.text
    print(city)
    mess = get_weather_box(city)
    bot.send_message(message.chat.id, mess, parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def date_from_user(message):
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


@bot.message_handler(commands=['history'])
def history(message):
    # если кто-то начинает использование то фунцкия берет его имя из бота, берет текущую дату
    # Записывает элементы и выводы в фаил.
    # Выдает фаил по запросу
    # так же может применяться для многозадачности, сохраняя конфиг запроса в личном файле, а не в классе

    name_id = f'{message.from_user.first_name}_{message.from_user.last_name}'
    print(message.from_user.id)

    try:
        with open(f'historys/{name_id}.json', 'r', encoding='utf-8') as r:
            print('b')
            fp = r.read(500)
            bot.send_message(message.from_user.id, fp)

            #rom = r.read().split('\n')
            #for el in rom:
             #   bot.send_message(message.from_user.id, el, parse_mode='JSON')
        bot.send_document(message.from_user.id, f'/historys/{name_id}.json')  # Какая будет дичь если заработает)
    except:
        bot.send_message(message.from_user.id, 'Вууф... почему-то я не могу найти твою историю')


#bot.enable_save_next_step_handlers(delay=2)
#bot.load_next_step_handlers()

#bot.polling(none_stop=True)


#  logger = telebot.logger
#  telebot.logger.setLevel(logging.DEBUG)
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

bot.infinity_polling(skip_pending=True)
