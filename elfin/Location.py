#!/usr/bin/python3

class Location():

    def __init__(self, id):
        self.__id = id
        self.__energy_meters = []
    
    def add_energy_meter(self, new_energy_meter):
        self.__energy_meters.append(new_energy_meter)

    def get_energy_meters(self):
        return self.__energy_meters

    def get_id(self):
        return self.__id