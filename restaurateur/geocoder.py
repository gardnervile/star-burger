import requests
from django.conf import settings
from requests.exceptions import RequestException

def fetch_coordinates_from_yandex(address):
    base_url = 'https://geocode-maps.yandex.ru/1.x/'
    try:
        response = requests.get(base_url, params={
            'geocode': address,
            'apikey': settings.YA_GEOCODER_API_KEY,
            'format': 'json',
        })
        response.raise_for_status()
    except RequestException:
        return None

    try:
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']
        if not found_places:
            return None

        point = found_places[0]['GeoObject']['Point']['pos']
        longitude, latitude = map(float, point.split())
        return latitude, longitude
    except (KeyError, ValueError, IndexError):
        return None
