
import requests
import json
import os
import re

# API key values
weather_api_key = os.environ['OPEN_WEATHER_MAP_API_KEY']
base_url = 'https://api.openweathermap.org/data/2.5/weather?zip='
country_code = 'GB'


def get_local_weather(post_code):
    post_code = re.sub(' ', '%20', post_code)
    url = base_url+post_code+','+country_code+'&appid='+weather_api_key
    request = requests.get(url)
    response = json.loads(request.content)
    # temperature in Celsius
    temperature = str(round(float(response['main']['temp']) - 273.15, 2))
    return temperature
