
import requests
import json
import os
import re

# API key values
weather_api_key = os.environ['OPEN_WEATHER_MAP_API_KEY']
base_url = 'https://api.openweathermap.org/data/2.5/weather?zip='
country_code = 'GB'


# from 'Flattening JSON objects in Python', Towards Data Science:
# https://towardsdatascience.com/flattening-json-objects-in-python-f5343c794b10
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out


# key code for flatten JSON weather data output
# 'coord_lon', 'coord_lat', 'weather_0_id', 'weather_0_main', 'weather_0_description',
# 'weather_0_icon', 'base', 'main_temp', 'main_feels_like', 'main_temp_min', 'main_temp_max',
# 'main_pressure', 'main_humidity', 'visibility', 'wind_speed', 'wind_deg', 'clouds_all',
# 'dt', 'sys_type' 'sys_id', 'sys_country', 'sys_sunrise', 'sys_sunset', 'timezone',
# 'id', 'name', 'cod'
def get_local_weather(post_code):
    weather_data = {}
    # https://stackoverflow.com/questions/13648729/python-regular-expression-for-outward-uk-post-code
    pattern = r'[A-Z]{1,2}[0-9R][0-9A-Z]?\s[0-9][A-Z]{2}'
    try:
        if re.findall(pattern, post_code):
            post_code = re.sub(' ', '%20', post_code)
            url = base_url+post_code+','+country_code+'&appid='+weather_api_key+'&units=metric'
            api_request = requests.get(url)
            api_response = json.loads(api_request.content)
            flatten_response = flatten_json(api_response)
            # temperature in Celsius
            weather_data['temperature'] = str(flatten_response['main_temp'])
            # pressure
            weather_data['pressure'] = str(flatten_response['main_pressure'])
    except Exception as e:
        print(e.__doc__)
    return weather_data
