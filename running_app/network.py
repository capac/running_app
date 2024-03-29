
import requests
import json
import os
import re
from datetime import datetime

# API key values
weather_api_key = os.environ['OPEN_WEATHER_MAP_API_KEY']
base_url = 'https://api.openweathermap.org/data/2.5/weather?zip='


# from 'Flattening JSON objects in Python', Towards Data Science:
# https://towardsdatascience.com/flattening-json-objects-in-python-f5343c794b10
def _flatten_json(y):
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


def _validate_post_code(post_code):
    '''validate post code according to format below before using it'''

    # https://stackoverflow.com/questions/13648729/python-regular-expression-for-outward-uk-post-code
    pattern = r'[A-Z]{1,2}[0-9R][0-9A-Z]?\s[0-9][A-Z]{2}'
    if not re.findall(pattern, post_code):
        raise Exception(
            '''Post code isn't in valid format'''
        )
    else:
        post_code = re.sub(' ', '%20', post_code)
    return post_code


# key code for flatten JSON weather data output
# 'coord_lon', 'coord_lat', 'weather_0_id', 'weather_0_main',
# 'weather_0_description', 'weather_0_icon', 'base', 'main_temp',
# 'main_feels_like', 'main_temp_min', 'main_temp_max',
# 'main_pressure', 'main_humidity', 'visibility', 'wind_speed',
# 'wind_deg', 'clouds_all', 'dt', 'sys_type' 'sys_id', 'sys_country',
# 'sys_sunrise', 'sys_sunset', 'timezone', 'id', 'name', 'cod'
def get_weather(post_code, country_code):
    weather_data = {}
    # units are metric
    first_url_part = f'{base_url}{_validate_post_code(post_code)},'
    second_url_part = f'{country_code}&appid={weather_api_key}&units=metric'
    url = first_url_part+second_url_part
    api_request = requests.get(url)
    api_response = json.loads(api_request.content)

    f_out = _flatten_json(api_response)
    # main weather information
    weather_data['weather_0_main'] = str(f_out['weather_0_main'])
    weather_data['main_temp'] = str(round(f_out['main_temp'], 1))
    weather_data['main_feels_like'] = str(round(f_out['main_feels_like'], 1))
    weather_data['pressure'] = str(f_out['main_pressure'])
    weather_data['humidity'] = str(f_out['main_humidity'])
    weather_data['visibility'] = str(f_out['visibility'])
    weather_data['wind_speed'] = str(f_out['wind_speed'])
    weather_data['wind_deg'] = str(f_out['wind_deg'])
    # convert from POSIX time to naive time
    for response in ['sys_sunrise', 'sys_sunset']:
        weather_data[response] = str(datetime.strftime(datetime.fromtimestamp(
                                     f_out[response]), '%H:%M'))
    return weather_data
