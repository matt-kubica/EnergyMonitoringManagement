#!/usr/bin/python3

import logging
import psycopg2
import sys
import time
import numpy as np
import os

from utils import DataTypes, FunctionCodes
from exceptions import UnknownDatatypeException, UnknownFunctioncodeException, ReadError

from pymodbus.client.sync import ModbusTcpClient
from influxdb import InfluxDBClient
from psycopg2 import DatabaseError
from apscheduler.schedulers.background import BackgroundScheduler


log_file                        = 'info.log'


class EnergyMeter():

    def __init__(self, type, description, modbus_client):
        self.type = type
        self.description = description
        self.modbus_client = modbus_client


class ModbusClient(ModbusTcpClient):

    def __init__(self, host, port, slave_address):
        self.host = host
        self.port = port
        self.slave_address = slave_address
        ModbusTcpClient.__init__(self, host=host, port=port)
        if not self.connect():
            raise ConnectionError('Cannot connect to {0}:{1}'.format(host, port))

    def convert(self, registers, data_type):
        if data_type == DataTypes.INT:
            return registers[0]
        elif data_type == DataTypes.FLOAT:
            tmp = np.array(registers, np.int16)
            tmp.dtype = np.float32
            return tmp[0]
        else:
            tmp = np.array(registers, np.int16)
            tmp.dtype = np.int32
            return tmp[0]

    def get_value(self, register_address, function_code, data_type):
        response = None
        bytes_count = None

        if data_type in (DataTypes.LONG, DataTypes.FLOAT):
            bytes_count = 2
        elif data_type in (DataTypes.INT, ):
            bytes_count = 1
        else:
            raise UnknownDatatypeException('Unknown data type with id: {0}'.format(data_type))

        if function_code == FunctionCodes.READ_INPUT_REGISTERS:
            response = self.read_input_registers(address=register_address, count=bytes_count, unit=self.slave_address)
        elif function_code == FunctionCodes.READ_HOLDING_REGISTERS:
            response = self.read_input_registers(address=register_address, count=bytes_count, unit=self.slave_address)
        else:
            raise UnknownFunctioncodeException('Unknown function code: {0}'.format(function_code))

        if response.isError():
            raise ReadError('Cannot get value from register: {0}, slave_address: {1}'.format(register_address, self.slave_address))

        return self.convert(response.registers, data_type)






class InfluxUpdater():

    def __init__(self):
        self.__logger_config()
        self.__scheduler_config()


    def __logger_config(self):
        self.__logger = logging.getLogger(__name__)
        file_handler = logging.FileHandler(log_file)
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s\t%(filename)s\t%(levelname)s\t%(message)s')

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(stream_handler)
        self.__logger.setLevel(logging.DEBUG)


    def __scheduler_config(self):
        self.__scheduler = BackgroundScheduler()

        params = {
            'hour': os.environ.get("CRON_HOUR_TRIGGER", "*"),
            'minute': os.environ.get("CRON_MINUTE_TRIGGER", "*/5"),
            'second': os.environ.get("CRON_SECOND_TRIGGER", "0"),
        }
        print(params)

        self.__main_job = self.__scheduler.add_job(**params, func=self.__main_task, trigger='cron')
        self.__logger.debug('Configured scheduler...')



    def __connect_influx(self):
        self.__influx_client = None

        params = {
            'host': os.environ.get("INFLUXDB_HOSTNAME"),
            'port': os.environ.get("INFLUXDB_PORT"),
            'database': os.environ.get("INFLUXDB_DB"),
            'username': os.environ.get("INFLUXDB_ADMIN_USER"),
            'password': os.environ.get("INFLUXDB_ADMIN_PASSWORD"),
        }

        try:
            self.__influx_client = InfluxDBClient(**params, timeout=10)
            self.__influx_client.request(url='ping', expected_response_code=204)
            self.__logger.debug('Successfully connected to influx...')
        except (ConnectionError, Exception) as err:
            self.__logger.error(err)

    def __disconnect_influx(self):
        self.__influx_client.close()
        self.__logger.debug('Successfully disconnected from influx...')


    def __connect_psql(self):
        params = {
            'host': os.environ.get("POSTGRES_HOST"),
            'port': os.environ.get("POSTGRES_PORT"),
            'database': os.environ.get("POSTGRES_DB"),
            'user': os.environ.get("POSTGRES_USER"),
            'password': os.environ.get("POSTGRES_PASSWORD"),
        }

        self.__psql_client = psycopg2.connect(**params)
        self.__logger.debug('Successfully connected to psql...')


    def __disconnect_psql(self):
        self.__psql_client.close()
        self.__logger.debug('Successfully disconnected from psql...')



    def __get_energy_meters(self):
        self.__energy_meters = []
        QUERY = 'SELECT * FROM energy_meters;'

        try:
            self.__connect_psql()
            cursor = self.__psql_client.cursor()
            cursor.execute(QUERY)
        except (Exception, DatabaseError) as err:
            self.__logger.error(err)
        else:
            for energy_meter_data in cursor.fetchall():
                new_modbus_client = ModbusClient(host=energy_meter_data[0], port=energy_meter_data[1], slave_address=energy_meter_data[2])
                new_energy_meter = EnergyMeter(type=energy_meter_data[3], description=energy_meter_data[4], modbus_client=new_modbus_client)
                self.__energy_meters.append(new_energy_meter)
            cursor.close()
            self.__disconnect_psql()

        if(not self.__energy_meters):
            self.__logger.debug('Energy meter list is empty...')
        else:
            self.__logger.debug('Updated energy meter list...')




    def __get_registers(self, energy_meter_type):
        QUERY = 'SELECT * FROM registers WHERE type = \'{0}\';'.format(energy_meter_type)

        try:
            self.__connect_psql()
            cursor = self.__psql_client.cursor()
            cursor.execute(QUERY)
            data = cursor.fetchall()
        except (Exception, DatabaseError) as err:
            self.__logger.error(err)
        else:
            cursor.close()
        self.__disconnect_psql()
        return data


    def __update_influx(self):
        self.__get_energy_meters()
        self.__connect_influx()

        for energy_meter in self.__energy_meters:
            registers = self.__get_registers(energy_meter.type)
            data_points_list = []
            for register in registers:
                address = register[1]
                measurement = register[2]
                dataunit = register[3]
                datatype = register[4]
                functioncode = register[5]
                value = None

                try:
                    value = energy_meter.modbus_client.get_value(register_address=address, function_code=functioncode, data_type=datatype)
                    data_point = {
                        'measurement': str(measurement),
                        'tags': {
                            'host': str(energy_meter.modbus_client.host),
                            'port': str(energy_meter.modbus_client.port),
                            'slave_address': str(energy_meter.modbus_client.slave_address),
                            'description': str(energy_meter.description),
                            'dataunit': str(dataunit),
                        },
                        'fields': {
                            'value': value
                        }
                    }
                    data_points_list.append(data_point)
                except (UnknownFunctioncodeException, ReadError, UnknownDatatypeException) as err:
                    self.__logger.error('Host: {0}, Port: {1}, Slaveaddress: {2} => ModbusClientException: {3} ({4})'.format(
                        energy_meter.modbus_client.host,
                        energy_meter.modbus_client.port,
                        energy_meter.modbus_client.slave_address,
                        err, measurement)
                    )

            if (not self.__influx_client.write_points(data_points_list)):
                self.__logger.error('Cannot write to influx...')
            data_points_list.clear()
            self.__logger.debug('Updated influx with data from {0}:{1}:{2}'.format(
                energy_meter.modbus_client.host,
                energy_meter.modbus_client.port,
                energy_meter.modbus_client.slave_address)
            )

        self.__disconnect_influx()


    def __main_task(self):
        try:
            self.__update_influx()
        except Exception as exc:
            self.__logger.error('Unusual exception: ' + str(exc))


    def start(self):
        self.__scheduler.start()
        self.__logger.info('Program started...')
        while(True):
            time.sleep(1)


    def stop(self):
        self.__scheduler.pause()




if __name__ == '__main__':
    influx_updater = InfluxUpdater()
    influx_updater.start()