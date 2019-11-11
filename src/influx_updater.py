#!/usr/local/bin/python3

import logging
import psycopg2
import sys
import time

from pyModbusTCP.client import ModbusClient as TCPModbusClient
from pyModbusTCP import utils
from influxdb import InfluxDBClient
from configparser import ConfigParser
from influx_updater_errors import ModbusClientException, FunctioncodeException, ReadError, UnknownDatatypeException, ParserException, InfluxError
from psycopg2 import DatabaseError
from apscheduler.schedulers.background import BackgroundScheduler



config_file                     = 'config.ini'
log_file                        = 'info.log'

# TODO: comments, tests - checkout all exceptions handling, add service

class EnergyMeter():

    def __init__(self, client_id, type, description, modbus_client):
        self.__client_id = client_id
        self.__type = type
        self.__description = description
        self.__modbus_client = modbus_client

    def get_client_id(self):
        return self.__client_id

    def get_type(self):
        return self.__type

    def get_description(self):
        return self.__description

    def get_host(self):
        return self.__modbus_client.get_host()

    def get_port(self):
        return self.__modbus_client.get_port()

    def get_slaveaddress(self):
        return self.__modbus_client.get_slaveaddress()

    def get_register_data(self, address, datatype, functioncode):
        return self.__modbus_client.get_register_data(address=address, datatype=datatype, functioncode=functioncode)




class ModbusClient(TCPModbusClient):

    def __init__(self, host, port, slaveaddress, timeout=1):
        self.__host = host
        self.__port = port
        self.__slaveaddress = slaveaddress
        TCPModbusClient.__init__(self, host=host, port=port, unit_id=slaveaddress, timeout=timeout, auto_open=True)

    def get_host(self):
        return self.__host

    def get_port(self):
        return self.__port

    def get_slaveaddress(self):
        return self.__slaveaddress

    # raises UnknownDatatypeException, ReadError, FunctioncodeException
    def get_register_data(self, address, datatype, functioncode):
        if (datatype == 'float'):
            return self.__read_float(address, functioncode)
        elif (datatype == 'int'):
            return self.__read_int(address, functioncode)
        elif (datatype == 'long'):
            return self.__read_long(address, functioncode)
        else:
            raise UnknownDatatypeException('Unknown datatype: ' + str(datatype))

    def __read_float(self, address, functioncode):
        if (functioncode == 3):
            register = self.read_holding_registers(reg_addr=address, reg_nb=2)
            if register:
                return utils.decode_ieee(utils.word_list_to_long(register)[0])
            else:
                raise ReadError('Error during reading register: ' + str(address))
        elif (functioncode == 4):
            register = self.read_input_registers(reg_addr=address, reg_nb=2)
            if register:
                return  utils.decode_ieee(utils.word_list_to_long(register)[0])
            else:
                raise ReadError('Error during reading register: ' + str(address))
        else:
            raise FunctioncodeException('Undefined functioncode: ' + str(functioncode))

    def __read_int(self, address, functioncode):
        if (functioncode == 3):
            register = self.read_holding_registers(reg_addr=address, reg_nb=1)
            if register:
                return register[0]
            else:
                raise ReadError('Error during reading register: ' + str(address))
        elif (functioncode == 4):
            register = self.read_input_registers(reg_addr=address, reg_nb=1)
            if register:
                return register[0]
            else:
                raise ReadError('Error during reading register: ' + str(address))
        else:
            raise FunctioncodeException('Undefined functioncode: ' + str(functioncode))

    def __read_long(self, address, functioncode):
        if (functioncode == 3):
            register = self.read_holding_registers(reg_addr=address, reg_nb=2)
            if register:
                return utils.word_list_to_long(register)[0]
            else:
                raise ReadError('Error during reading register: ' + str(address))
        elif (functioncode == 4):
            register = self.read_input_registers(reg_addr=address, reg_nb=2)
            if register:
                return utils.word_list_to_long(register)[0]
            else:
                raise ReadError('Error during reading register: ' + str(address))
        else:
            raise FunctioncodeException('Undefined functioncode: ' + str(functioncode))




class InfluxUpdater():

    def __init__(self, config_file, log_file):
        self.__config_file = config_file
        self.__log_file = log_file
        self.__logger_config()
        self.__connect_influx()
        self.__connect_psql()
        self.__scheduler_config()


    def __logger_config(self):
        self.__logger = logging.getLogger(__name__)
        file_handler = logging.FileHandler(self.__log_file)
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s\t%(filename)s\t%(levelname)s\t%(message)s')

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(stream_handler)
        self.__logger.setLevel(logging.INFO)


    def __scheduler_config(self):
        self.__scheduler = BackgroundScheduler()
        params = self.__get_config('scheduler')
        self.__main_job = self.__scheduler.add_job(**params, func=self.__update_influx, trigger='cron')



    def __get_config(self, section):
        parser = ConfigParser()
        parser.read(self.__config_file)

        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise ParserException
        return db


    def __connect_influx(self):
        self.__influx_client = None
        try:
            params = self.__get_config('influx')
            self.__influx_client = InfluxDBClient(**params, timeout=10)
            self.__influx_client.request(url='ping', expected_response_code=204)
            self.__logger.info('Successfully connected to influx...')
        except (ParserException, ConnectionError, Exception) as err:
            self.__logger.error(err)


    def __connect_psql(self):
        self.__psql_client = None
        try:
            params = self.__get_config('psql')
            self.__psql_client = psycopg2.connect(**params)
            self.__logger.info('Successfully connected to psql...')
        except (Exception, DatabaseError) as err:
            self.__logger.error(err)


    def __get_energy_meters(self):
        self.__energy_meters = []

        cursor = self.__psql_client.cursor()
        cursor.execute('SELECT * FROM energy_meters;')
        for energy_meter_data in cursor.fetchall():
            new_modbus_client = ModbusClient(host=energy_meter_data[1], port=energy_meter_data[2], slaveaddress=energy_meter_data[3])
            new_energy_meter = EnergyMeter(client_id=energy_meter_data[0], type=energy_meter_data[4], description=energy_meter_data[5], modbus_client=new_modbus_client)
            self.__energy_meters.append(new_energy_meter)


    def __get_registers(self, energy_meter_type):
        cursor = self.__psql_client.cursor()
        query = 'SELECT registers.address, registers.measurement, registers.dataunit, registers.datatype, registers.functioncode FROM registers WHERE registers.energy_meter_id = \'' + str(energy_meter_type) + '\';'
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data


    def __update_influx(self):
        self.__get_energy_meters()
        for energy_meter in self.__energy_meters:
            registers = self.__get_registers(energy_meter.get_type())
            data_points_list = []
            for register in registers:
                address = register[0]
                measurement = register[1]
                dataunit = register[2]
                datatype = register[3]
                functioncode = register[4]
                value = None

                try:
                    value = energy_meter.get_register_data(address=address, datatype=datatype, functioncode=functioncode)
                except (FunctioncodeException, ReadError, UnknownDatatypeException) as err:
                    self.__logger.error('Client: {0}, Host: {1}, Port: {2}, Slaveaddress: {3} => ModbusClientException: {4} ({5})'.format(
                                                energy_meter.get_client_id(), energy_meter.get_host(), energy_meter.get_port(),
                                                energy_meter.get_slaveaddress(), err, measurement))



                data_point = {
                    'measurement': str(measurement),
                    'tags': {
                        'dataunit': str(dataunit),
                        'energy_meter': str(energy_meter.get_type()),
                        'description': str(energy_meter.get_description()),
                        'client_id': str(energy_meter.get_client_id())
                    },
                    "fields": {
                        "value": value
                    }
                }
                data_points_list.append(data_point)
            if (not self.__influx_client.write_points(data_points_list)):
                self.__logger.error('Cannot write to influx...')
            data_points_list.clear()
        self.__logger.info('Data successfully wrote to influx...')


    def start(self):
        self.__scheduler.start()
        while(True):
            time.sleep(1)


    def stop(self):
        self.__scheduler.pause()




if __name__ == '__main__':
    influx_updater = InfluxUpdater(config_file=config_file, log_file=log_file)
    influx_updater.start()