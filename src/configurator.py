#!/usr/local/bin/python3

import logging
import psycopg2
from configparser import ConfigParser
from influx_updater_errors import ParserException, DatabaseError

class Configurator():

    def __init__(self, db_config_file, log_file):
        self.__db_config_file = db_config_file
        self.__log_file = log_file
        self.__logger_config()
        self.__connect_psql()


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
            self.__logger.error(err)

    def add_energy_meter(self, location_id, host, port, slaveaddress, energy_meter_id, description):
        cursor = self.__psql_client.cursor()
        query = '''INSERT INTO energy_meters VALUES({0}, '{1}', {2}, {3}, '{4}', '{5}')'''.format(location_id, host, port, slaveaddress, energy_meter_id, description)
        print(query)