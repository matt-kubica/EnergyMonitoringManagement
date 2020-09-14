
import sys
import time
import logging
import requests
import json
import numpy as np

from pyModbusTCP.server import ModbusServer, DataBank
from apscheduler.schedulers.background import BackgroundScheduler


INVERTER_HOST                     = '178.218.234.100'
INVERTER_PORT                     = '2138'
INVERTER_URL                      = 'http://' + INVERTER_HOST + ':' + INVERTER_PORT + '/home.cgi?sid=0'

API_KEY                           = '9d10bedba49340a28aa0a8664d2ee7f0'
API_URL                           = 'https://www.zevercloud.com/api/v1/getPlantOverview'

logger                            = None
log_file                          = 'info.log'


class InverterConnectionError(Exception):
    pass

def logger_config():
    global logger
    logger = logging.getLogger(__name__)
    file_handler = logging.FileHandler(log_file)
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s\t%(filename)s\t%(levelname)s\t%(message)s')

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
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


def get_active_energy_and_power():

    power_AC = 0.0
    energy_today = 0.0
    inverter_request = None
    try:
        inverter_request = requests.get(INVERTER_URL, timeout=5)
    except requests.exceptions.ConnectionError:
        logger.warning('Cannot connect to inverter')
    else:
        parameter_list = list(inverter_request.text.split('\n'))
        power_AC = float(int(parameter_list[10]) / 1000)
        energy_today = float(parameter_list[11])


    api_request = None
    try:
        api_request = requests.get(API_URL, params = { 'key': API_KEY })
    except requests.exceptions.ConnectionError as err:
        if(api_request.status_code != requests.codes.ok):
            logger.error('Cannot connect with zevercloud: ' + str(err))
            raise InverterConnectionError
    else:
        energy_total = recalculate_values(json.loads(api_request.text)['E-Total']['value'], json.loads(api_request.text)['E-Total']['unit'])
        logger.debug(energy_total)
        return (power_AC, energy_today, energy_total)


def float_to_registers(number):
    tmp = np.array([number], np.float32)
    tmp.dtype = np.int16
    return tmp




def set_databank_words():

    active_power = None
    active_energy_produced_today = None
    active_energy_produced_total = None

    try:
        (active_power, active_energy_produced_today, active_energy_produced_total) = get_active_energy_and_power()
    except InverterConnectionError:
        pass


    DataBank.set_words(0, float_to_registers(active_power))
    DataBank.set_words(2, float_to_registers(active_energy_produced_today))
    DataBank.set_words(4, float_to_registers(active_energy_produced_total)) 



if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-H", "--host", type=str, default="0.0.0.0", help="host")
    # parser.add_argument("-p", "--port", type=int, default=502, help="port")
    # args = parser.parse_args()
    logger_config()

    modbus_server = ModbusServer(host="0.0.0.0", port=502, no_block=True)
    modbus_server.start()
    logger.debug('Server started!')

    scheduler = BackgroundScheduler()
    scheduler.add_job(set_databank_words, trigger="cron", minute="*")
    scheduler.start()

    while True:
        time.sleep(1)

