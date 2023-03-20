from config import hotels_token
import requests
import pprint
import datetime

url_base = "https://hotels4.p.rapidapi.com/locations/v3/search"
headers = hotels_token


def get_hotels(city):
    nearby_hotel = []
    try:
        querystring = {"q": f"{city}", "locale": "ru_RU"} # f"{MyStates.city}"
        response = requests.request("GET", url_base, headers=headers, params=querystring, timeout=10)
        data = response.json()
        for i in range(len(data['sr'])):
            hotel_name = data['sr'][i]['regionNames']['fullName']
            print(hotel_name)
            hotel_address = data['sr'][i]['hotelAddress']['street']
            mess = f'🗺️У нас тут есть <b>{hotel_name}</b>\n🏡По адресу {hotel_address}'
            nearby_hotel.append([mess])

        return nearby_hotel

    except:
        nearby_hotel.append('Тут увы я не смогу разнюхать прямо сейчас')
