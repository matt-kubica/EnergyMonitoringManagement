#!/usr/bin/python3

class EnergyMeter():

    def __init__(self, type, description, modbus_client):
        self.__type = type
        self.__description = description
        self.__modbus_client = modbus_client
    
    def get_type(self):
        return self.__type

    def get_description(self):
        return self.__description

    def get_register_data(self, address, datatype, functioncode):
        return self.__modbus_client.get_register_data(address = address, datatype = datatype, functioncode = functioncode)