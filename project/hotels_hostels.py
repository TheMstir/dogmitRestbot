from config import hotels_token
import requests

url_base = "https://hotels4.p.rapidapi.com/locations/v3/search"
url_list = "https://hotels4.p.rapidapi.com/properties/v2/list"
url_data = "https://hotels4.p.rapidapi.com/properties/v2/detail"
headers = hotels_token


def get_hotels_box(city: str, count_place: int, count_photo: int, flag: str) -> list:
    list_view = [[f'🐶А вот и список гостиниц по вашему запросу в: {city}'], ]
    little_photo_list = []

    #  cначала получаем ID географической метки в базе, более-менее универсальный параметр нашел только тут
    try:
        querystring = {"q": f"{city}", "locale": "ru_RU"}  # locate можно переназначить на получение
        # информации от языка установленного в телеграмме
        response = requests.request("GET", url_base, headers=headers, params=querystring, timeout=10)
        data = response.json()

        try:
            gaiaid = data['sr'][0]['gaiaId']  # пытаемся получить геоидентификатор
        except:
            ex = ['Увы, тут я сейчас разнюхать не могу❓\nКто-то все спрятал...🚷\n'
                  'пойдем в /help, что-нибудь придумаем🔙']
            list_view.append(ex)
            return list_view

        payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "en_EN",
            "siteId": 300000001,
            "destination": {"regionId": f'{gaiaid}'},
            "checkInDate": {
                "day": 10,
                "month": 10,
                "year": 2022
            },
            "checkOutDate": {
                "day": 11,
                "month": 10,
                "year": 2022
            },
            "rooms": [
                {
                    "adults": 1
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": 25,
            "sort": f"{flag}",
            "filters": {"price": {
                "max": 200,
                "min": 20
            }}
        }

        response_2 = requests.request("POST", url_list, json=payload, headers=headers)
        data_2 = response_2.json()
        for i in range(count_place):
            name = data_2['data']['propertySearch']['properties'][i]['name']
            hotel_id = data_2['data']['propertySearch']['properties'][i]['id']
            stars = data_2['data']['propertySearch']['properties'][i]['reviews']['score']
            url_photo = data_2['data']['propertySearch']['properties'][i]['propertyImage']['image']['url']
            price = data_2['data']['propertySearch']['properties'][i]['mapMarker']['label']
            coordinates_lat = data_2['data']['propertySearch']['properties'][i]['mapMarker']['latLong']['latitude']
            coordinates_lon = data_2['data']['propertySearch']['properties'][i]['mapMarker']['latLong']['longitude']
            dest_from_center = data_2['data']['propertySearch']['properties'][i]['destinationInfo']['distanceFromDestination']['value']*1.602
            #  сделать универсальное начало для последних 3х переменных

            payload = {
                "currency": "USD",
                "eapid": 1,
                "locale": "en_US",
                "siteId": 300000001,
                "propertyId": f"{hotel_id}"
            }

            response_3 = requests.request("POST", url_data, json=payload, headers=headers)
            data_3 = response_3.json()
            address = data_3['data']['propertyInfo']['summary']['location']['address']['addressLine']
            tag = data_3['data']['propertyInfo']['summary']['tagline']

            for j in range(count_photo):
                photo = data_3['data']['propertyInfo']['propertyGallery']['images'][j]['image']['url']
                little_photo_list.append(photo)

            mess = f"Отель <b>{name}</b>, с оценкой в {stars}⭐,\n" \
                   f"Описывается как: {tag}\nCредняя цена💲 за сутки: " \
                   f"{price}\n🌎Географически расположен {coordinates_lat}, {coordinates_lon}\n" \
                   f"🗺️То есть по адресу: {address}\n" \
                   f"Что находиться в {int(dest_from_center)}км.\n от центра города 🏬" \
                   f"🏢Если будете искать то смотрите такое здание: {url_photo}"
            # считаю визуально необходимым прикрепить хотя бы одно фото к выдаче в виде ссылки
            # оставил доп знаки чтобы вытащить координаты регулярками и в дальнейшем передать их

            if count_photo == 0:
                list_view.append([mess])

            if count_photo > 0:
                list_view.append([mess, little_photo_list])
                little_photo_list = []  # очищаем промежуточный список чтобы наверняка не переносить фотки в допы

        return list_view

    except Exception as exeption:
        print(exeption)
        mess = 'Вуф! Что-то пошло не так, уже пытаюсь решить...\n🐶 но у меня же лапки\nКто-то все спрятал...🚷\n' \
               'пойдем в /help, что-нибудь придумаем🔙'
        list_view.append(mess)
        return list_view

# Функция с циклом по количеству показываемых объектов, надо будет отправлять каждый
# Если фото то дополнительно качать

