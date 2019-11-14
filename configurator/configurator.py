#!/usr/local/bin/python3

import logging
import psycopg2
import sys
import time
from psycopg2 import DatabaseError
from configparser import ConfigParser
from configurator_errors import ParserException
from apscheduler.schedulers.background import BackgroundScheduler

from psycopg2.errors import AdminShutdown
from psycopg2 import InterfaceError


log_file = 'info.log'
config_file = 'config.ini'


class Configurator():

    def __init__(self, db_config_file, log_file):
        self.__db_config_file = db_config_file
        self.__log_file = log_file
        self.__logger_config()
        self.__connect_psql()
        self.__scheduler_config()

    def __scheduler_config(self):
        self.__scheduler = BackgroundScheduler()
        params = self.__get_config('scheduler')
        self.__main_job = self.__scheduler.add_job(**params, func=self.__main_task, trigger='cron')
        self.__scheduler.start()

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


    def __get_config(self, section):
        parser = ConfigParser()
        parser.read(self.__db_config_file)

        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise ParserException
        return db

    def __connect_psql(self):
        self.__psql_client = None
        try:
            params = self.__get_config('psql')
            self.__psql_client = psycopg2.connect(**params)
            self.__logger.info('Successfully connected to psql...')
        except (Exception, DatabaseError) as err:
            self.__logger.error('Cannot connect to psql...')
            sys.exit(1)

    # TODO: valid parameters
    def add_energy_meter(self, location_id, host, port, slaveaddress, energy_meter_id, description):
        query = '''INSERT INTO energy_meters(location_id, host, port, slaveaddress, energy_meter_id, description) 
                   VALUES({0}, '{1}', {2}, {3}, '{4}', '{5}');''' \
                   .format(location_id, host, port, slaveaddress, energy_meter_id, description)
        try:
            cursor = self.__psql_client.cursor()
            cursor.execute(query)
            self.__psql_client.commit()
            self.__logger.info(query)
            cursor.close()
        except (AdminShutdown, InterfaceError, Exception) as exc:
            self.__logger.error('Unexpected psql disconnect, exiting...')
            self.__scheduler.shutdown()
        finally:
            sys.exit(-1)


    def __main_task(self):
        self.add_energy_meter(location_id=2, host='0.0.0.0', port=502, slaveaddress=1, energy_meter_id='sdm630', description='test_energy_meter')


if __name__ == '__main__':
    c = Configurator(config_file, log_file)
    # c.add_energy_meter(location_id=2, host='0.0.0.0', port=502, slaveaddress=1, energy_meter_id='sdm630', description='test_energy_meter')
    while(True):
        time.sleep(1)