import requests
import json
import datetime
import config
import telebot

# Фаил и разместить ссылку


def get_weather_box(city):
    """
    По запросу выводит краткие подсказки по погоде в городе, где пользователь ищет отель.

    :param Принимает город поиска отеля и определяет погодные условия, время заката, силу ветра
    Выводит краткое сообщение с минимально необходимыми для определения данными
    """
    weather_token = config.weather_token  # позднее перенести конфиги в отдельный

    try:
        weather_r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_token}"
                                 f"&units=metric", timeout=10)
        data = weather_r.json()

        city = data['name'] # получаем название города
        coord = data['coord']
        cur_w = data['main']['temp'] # текущая погода в городе
        feels_like = data['main']['feels_like'] # погода "по-ощущениям"
        wind = data['wind']['speed'] # сила ветра
        emoj = data['weather'][0]['description'] # замена описания погоды на подходящую эмоджи
        sunset = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        current_time = datetime.datetime.now() # время по часам программы

        delta = datetime.timedelta(seconds=data['timezone'])
        tz = datetime.timezone(delta, str(data['timezone']))
        current_time_place = datetime.datetime.now(tz=tz)

# выкинуть в отдельную функцию этот элемент
        if emoj == 'clear sky':
            emoj = '🌞'
        elif emoj == 'rain':
            emoj = '🌧️'
        elif emoj == 'snow':
            emoj = '❄️'
        else:
           # emoji == emoj
            pass
            # Доделать

        mounth = {1: 'январь ❄️', 2: 'февраль ❄️', 3: 'март 🌼', 4: 'апрель 🌼', 5: 'май 🌼', 6: 'июнь ☀️',
                  7: 'июль ☀️', 8: 'август ☀️', 9: 'сентябрь 🍂', 10: 'октябрь 🍂', 11: 'ноябрь 🍂', 12: 'декабрь ❄️'}

        mess = f'''В {city} 🏙️ сейчас {mounth.get(current_time_place.month)} месяц, {current_time_place.day} число'
              \n⏱️{current_time_place.hour} часов, {current_time_place.minute} минут'
              \n🌡️{cur_w}°C, ощущается как {feels_like}°C. {emoj}, сила ветра: {wind} 💨'
              \nСолнце уйдет за горизонт в {sunset} 🌇'
              \nНадеюсь это поможет определиться с размещением, гав! 🐶'''

    except Exception as exeption:
        print(exeption)
        mess = 'Погоду не подскажу, не понимаю где этот город 🦴'

    return mess
        # https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}



def start_weather(city):
      # позднее буду получать от запроса на город и давать дополнительный совет по погоде\
    return get_weather(city)
