#!/usr/bin/python3

import logging
import psycopg2
import sys
import time
import os

from utils import DataTypes, FunctionCodes, EndianOrder
from exceptions import UnknownDatatypeException, UnknownFunctioncodeException, ReadError
from energy_meter import EnergyMeter, Register, ModbusClient

from influxdb import InfluxDBClient
from psycopg2 import DatabaseError
from apscheduler.schedulers.background import BackgroundScheduler


        


class InfluxUpdater():

    def __init__(self):
        self.logger_config()
        self.scheduler_config()
        self.energy_meters = []


    def logger_config(self):
        self.logger = logging.getLogger(__name__)
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s\t%(filename)s\t%(levelname)s\t%(message)s')
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.DEBUG)


    def scheduler_config(self):
        self.scheduler = BackgroundScheduler()

        cron_params = {
            'hour': os.environ.get("SCHEDULER_CRON_HOUR_TRIGGER"),
            'minute': os.environ.get("SCHEDULER_CRON_MINUTE_TRIGGER"),
            'second': os.environ.get("SCHEDULER_CRON_SECOND_TRIGGER"),
        }


        self.main_job = self.scheduler.add_job(**cron_params, func=self.main_task, trigger='cron')
        self.logger.debug('Configured scheduler...')



    def connect_influx(self):
        self.influx_client = None

        influx_params = {
            'host': os.environ.get("INFLUXDB_HOSTNAME"),
            'port': os.environ.get("INFLUXDB_PORT"),
            'database': os.environ.get("INFLUXDB_DB"),
            'username': os.environ.get("INFLUXDB_ADMIN_USER"),
            'password': os.environ.get("INFLUXDB_ADMIN_PASSWORD"),
        }

        try:
            self.influx_client = InfluxDBClient(**influx_params, timeout=10)
            self.influx_client.request(url='ping', expected_response_code=204)
            self.logger.debug('Successfully connected to influx...')
        except (ConnectionError, Exception) as err:
            self.logger.error(err)

    def disconnect_influx(self):
        self.influx_client.close()
        self.logger.debug('Successfully disconnected from influx...')



    def connect_psql(self):
        psql_params = {
            'host': os.environ.get("POSTGRES_HOST"),
            'port': os.environ.get("POSTGRES_PORT"),
            'database': os.environ.get("POSTGRES_DB"),
            'user': os.environ.get("POSTGRES_USER"),
            'password': os.environ.get("POSTGRES_PASSWORD"),
        }

        self.psql_client = psycopg2.connect(**psql_params)
        self.logger.debug('Successfully connected to psql...')



    def disconnect_psql(self):
        self.psql_client.close()
        self.logger.debug('Successfully disconnected from psql...')



    def get_energy_meters(self):
        energy_meters = []
        QUERY = 'SELECT * FROM energy_meters;'

        try:
            cursor = self.psql_client.cursor()
            cursor.execute(QUERY)
        except (Exception, DatabaseError) as err:
            self.logger.error(err)
        else:
            for energy_meter_data in cursor.fetchall():

                try:
                    new_modbus_client = ModbusClient(host=energy_meter_data[1], port=energy_meter_data[2], slave_address=energy_meter_data[3])
                    new_energy_meter = EnergyMeter(id=energy_meter_data[0], type=energy_meter_data[4], description=energy_meter_data[5], modbus_client=new_modbus_client)
                    energy_meters.append(new_energy_meter)
                except ConnectionError as err:
                    self.logger.warning('{0}, skipping...'.format(err))
                    continue

                
            cursor.close()

        if not energy_meters:
            self.logger.info('Energy meter list is empty...')
            return None
        else: 
            return energy_meters



    def get_registers(self, energy_meter_type):
        QUERY = 'SELECT * FROM registers WHERE type = \'{0}\';'.format(energy_meter_type)

        try:
            cursor = self.psql_client.cursor()
            cursor.execute(QUERY)
            data = cursor.fetchall()
        except (Exception, DatabaseError) as err:
            self.logger.error(err)
        else:
            cursor.close()
        
        registers = []
        for row in data:
            registers.append(Register(type=row[0], register_address=row[1], measurement_name=row[2], data_unit=row[3], data_type=row[4], function_code=row[5], word_order=row[6], byte_order=row[7]))

        return registers



    def main_task(self):

        cron_params = {
            'hour': os.environ.get("INFLUX_UPDATER_CRON_HOUR_TRIGGER"),
            'minute': os.environ.get("INFLUX_UPDATER_CRON_MINUTE_TRIGGER"),
            'second': os.environ.get("INFLUX_UPDATER_CRON_SECOND_TRIGGER"),
        }

        updated_energy_meter_list = self.get_energy_meters()
        new_energy_meters = list(set(updated_energy_meter_list) - set(self.energy_meters))
        removed_energy_meters = list(set(self.energy_meters) - set(updated_energy_meter_list))

        for energy_meter in new_energy_meters:
            self.energy_meters.append(energy_meter)
            self.scheduler.add_job(**cron_params, id=str(energy_meter.id), func=self.update_influx, args=[energy_meter], trigger='cron')
            self.logger.info('Added new energy meter: ({0})'.format(energy_meter))

        for energy_meter in removed_energy_meters:
            self.energy_meters.remove(energy_meter)
            self.scheduler.remove_job(str(energy_meter.id))
            self.logger.info('Removed energy meter: ({0})'.format(energy_meter))



    def update_influx(self, energy_meter):
        registers = self.get_registers(energy_meter.type)
        data_points_list = []

        for register in registers:
            value = None

            try:
                value = energy_meter.modbus_client.get_value(
                    register_address=register.register_address,
                    function_code=register.function_code,
                    data_type=register.data_type,
                    word_order=register.word_order, byte_order=register.byte_order)
                data_point = {
                    'measurement': str(register.measurement_name),
                    'tags': {
                        'id': str(energy_meter.id),
                        'description': str(energy_meter.description),
                        'dataunit': str(register.data_unit),
                    },
                    'fields': {
                        'value': float(value)
                    }
                }
                data_points_list.append(data_point)
            except (UnknownFunctioncodeException, ReadError, UnknownDatatypeException) as err:
                self.logger.warning('({0}) => ModbusClientException: {1} ({2})'.format(energy_meter, err, register.measurement_name))

        if not self.influx_client.write_points(data_points_list, time_precision='s'):
            self.logger.error('Cannot write to influx...')
        
        if len(data_points_list) != 0:
            self.logger.info('Updated influx with data from ({0})'.format(energy_meter))
        else:
            self.logger.info('No data retrieved from ({0})'.format(energy_meter))



    def start(self):
        self.connect_psql()
        self.connect_influx()
        self.scheduler.start()
        self.logger.info('Program started...')

        while True:
            time.sleep(1)




if __name__ == '__main__':
    influx_updater = InfluxUpdater()
    influx_updater.start()
