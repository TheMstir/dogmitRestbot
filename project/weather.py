import requests
import datetime
import config


def get_weather_box(city):
    """
    По запросу выводит краткие подсказки по погоде в городе, где пользователь ищет отель.

    Принимает город поиска отеля и определяет погодные условия, время заката, силу ветра
    Выводит краткое сообщение с минимально необходимыми для определения данными

    Переработка описания неба в эмоджи в процессе работы...
    """
    weather_token = config.weather_token  # позднее перенести конфиги в отдельный

    try:
        weather_r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_token}"
                                 f"&units=metric", timeout=10)
        data = weather_r.json()

        city = data['name'] # получаем название города
        coord = data['coord']
        cur_w = data['main']['temp'] # текущая погода в городе
        feels_like = data['main']['feels_like']  # погода "по-ощущениям"
        wind = data['wind']['speed'] # сила ветра
        emoj = data['weather'][0]['description']  # замена описания погоды на подходящую эмоджи
        sunset = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        current_time = datetime.datetime.now()  # время по часам программы

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
        elif emoj == 'overcast clouds' or 'broken clouds':
            emoj = '☁️'
        else:
           # emoji == emoj
            pass
            # Доделать

        mounth = {1: 'январь ❄️', 2: 'февраль ❄️', 3: 'март 🌼', 4: 'апрель 🌼', 5: 'май 🌼', 6: 'июнь ☀️',
                  7: 'июль ☀️', 8: 'август ☀️', 9: 'сентябрь 🍂', 10: 'октябрь 🍂', 11: 'ноябрь 🍂', 12: 'декабрь ❄️'}

        mess = f'В {city} 🏙️ сейчас {mounth.get(current_time_place.month)} месяц, {current_time_place.day} число\n' \
               f'⏱️{current_time_place.hour} часов, {current_time_place.minute} минут\n' \
               f'\n🌡️{cur_w}°C, ощущается как {feels_like}°C. {emoj}, сила ветра: {wind} 💨\n' \
               f'Солнце уйдет за горизонт {sunset} 🌇\n' \
               f'Надеюсь это поможет определиться с размещением, гав! 🐶'

    except Exception as exeption:
        print(exeption)
        mess = 'Погоду не подскажу, не понимаю где этот город 🦴'

    return mess
