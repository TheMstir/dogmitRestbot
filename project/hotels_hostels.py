import datetime

from config import hotels_token
import requests

url_base = "https://hotels4.p.rapidapi.com/locations/v3/search"
url_list = "https://hotels4.p.rapidapi.com/properties/v2/list"
url_data = "https://hotels4.p.rapidapi.com/properties/v2/detail"
headers = hotels_token


def get_hotels_box(city: str, count_place: int, count_photo: int, flag: str, date_in: str, date_out: str) -> list:
    list_view = [[f'🐶А вот и список гостиниц по вашему запросу в: {city}'], ]
    little_photo_list = []
    year_in, mounth_in, day_in = str(date_in).split('-')
    year_out, mounth_out, day_out = str(date_out).split('-')
    year_in = int(year_in)
    mounth_in = int(mounth_in)
    day_in = int(day_in)
    year_out = int(year_out)
    mounth_out = int(mounth_out)
    day_out = int(day_out)

    #  cначала получаем ID географической метки в базе, более-менее универсальный параметр нашел только тут
    try:
        querystring = {"q": f"{city}", "locale": "en_US"}  # locate можно переназначить на получение
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
            "locale": "en_US",
            "siteId": 300000001,
            "destination": {"regionId": f'{gaiaid}'},
            "checkInDate": {
                "day": day_in,
                "month": mounth_in,
                "year": year_in
            },
            "checkOutDate": {
                "day": day_out,
                "month": mounth_out,
                "year": year_out
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
                "max": 650,
                "min": 20
            }}
        }

        # возможно изменить ограничители сумм

        response_2 = requests.request("POST", url_list, json=payload, headers=headers)
        data_2 = response_2.json()
        for i in range(count_place):
            name = data_2['data']['propertySearch']['properties'][i]['name']
            hotel_id = data_2['data']['propertySearch']['properties'][i]['id']
            stars = data_2['data']['propertySearch']['properties'][i]['reviews']['score']
            coordinates_lat = data_2['data']['propertySearch']['properties'][i]['mapMarker']['latLong']['latitude']
            coordinates_lon = data_2['data']['propertySearch']['properties'][i]['mapMarker']['latLong']['longitude']
            dest_from_center = data_2['data']['propertySearch']['properties'][i]['destinationInfo']['distanceFromDestination']['value'] * 1.602
            for_one_night = \
                data_2['data']['propertySearch']['properties'][i]['price']['displayMessages'][0]['lineItems'][0]['price']['formatted']
            #  Возможно достаточно перемножить это число,
            for_all_night = \
                data_2['data']['propertySearch']['properties'][i]['price']['displayMessages'][1]['lineItems'][0]['value']

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
                   f"Описывается как: {tag}\n" \
                   f"Cредняя цена💲 за сутки: {for_one_night}, а за запрошенный вами срок, со " \
                   f"всеми налогами будет: {for_all_night} 💰\n" \
                   f"🌎Географически расположен {coordinates_lat}, {coordinates_lon}\n" \
                   f"🗺️То есть по адресу: {address}\n" \
                   f"Что находиться в {int(dest_from_center)}км.\n от центра города 🏬\n" \
                   f"🏢Вы можете узнать больше по ссылке:  " \
                   f"🌐 https://www.hotels.com/h{hotel_id}.Hotel-Information" \
                #  оставил много эмодзи чтобы вытащить координаты букв регулярками и в дальнейшем более удобно резать

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
