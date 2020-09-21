import os
import requests
import json
import logging
import sys


INVERTER_URL                      = 'http://' + os.environ.get("VIRTUAL_TLC10000_INVERTER_HOST") + ':' + os.environ.get("VIRTUAL_TLC10000_INVERTER_PORT") + '/home.cgi?sid=0'

API_KEY                           = os.environ.get("VIRTUAL_TLC10000_INVERTER_API_KEY")
API_URL                           = 'https://www.zevercloud.com/api/v1/getPlantOverview'


logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s\t%(filename)s\t%(levelname)s\t%(message)s')

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def recalculate_values(value, unit):
    if(unit == 'Wh'):
        value = float(value) / 1000
    elif(unit == 'MWh'):
        value = float(value) * 1000
    elif(unit == 'GWh'):
        value = float(value) * 1000000
    return value


def request_inverter():
    request_body = None

    try:
        request_body = requests.get(INVERTER_URL, timeout=5)
    except requests.exceptions.ConnectionError:
        logger.warning('Cannot connect to inverter')
    else:
        return request_body


def request_api():
    request_body = None

    try:
        request_body = requests.get(API_URL, params = { 'key': API_KEY })
    except requests.exceptions.ConnectionError as err:
        logger.warning('Cannot connect to API')
    else:
        return request_body


def get_power():
    request_body = request_inverter()
    parameter_list = list(request_body.text.split('\n'))
    return float(int(parameter_list[10]) / 1000)


def get_energy_today():
    request_body = request_inverter()
    parameter_list = list(request_body.text.split('\n'))
    return float(parameter_list[11])


def get_energy_total():
    request_body = request_api()
    return recalculate_values(json.loads(request_body.text)['E-Total']['value'], json.loads(request_body.text)['E-Total']['unit'])

