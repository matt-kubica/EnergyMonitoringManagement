#!/usr/bin/python3

import sqlite3

class InfluxUpdater():

    def __init__(self, db_client, locations, sqlite_config_path):
        self.__db_client = db_client
        self.__loactions = locations
        self.__sqlite_config_path = sqlite_config_path

    def set_db(self, new_db_client):
        self.__db_client = new_db_client

    def add_location(self, new_location):
        self.__loactions.append(new_location)

    def __get_registers(self, energy_meter_type):
        connection = sqlite3.connect(self.__sqlite_config_path)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM ' + str(energy_meter_type))
        return cursor.fetchall()
        
    def update_influx(self):
        for location in self.__loactions:
            for energy_meter in location.get_energy_meters():
                registers = self.__get_registers(energy_meter.get_type())
                data_points_list = []
                for register in registers:
                    address = register[0]
                    measurement = register[1]
                    dataunit = register[2]
                    datatype = register[3]
                    functioncode = register[4]

                    value = energy_meter.get_register_data(address = address, datatype = datatype, functioncode = functioncode)

                    data_point = {
                        'measurement': str(measurement),
                        'tags': {
                            'dataunit': str(dataunit),
                            'location_id': str(location.get_id()),
                            'energy_meter': str(energy_meter.get_type()),
                            'description': str(energy_meter.get_description())
                        },
                        "fields": {
                            "value": value
                        }
                    }
                    data_points_list.append(data_point)
                if(not self.__db_client.write_points(data_points_list)):
                    raise SomeError
                data_points_list.clear()
            
