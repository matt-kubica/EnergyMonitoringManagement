#!/usr/bin/python3.7
from configparser import ConfigParser

from ModbusClient import ModbusClient
import psycopg2
from influxdb import InfluxDBClient


def modbus():
    m = ModbusClient(host='192.168.1.20', port=502, slaveaddress=1, timeout=10)
    # print(m.get_register_data(address=0, datatype='float', functioncode=4))
    try:
        x = m.get_register_data(address=0, datatype='float', functioncode=4)
        print(x)
    except Exception as err:
        print(err)

def psql():
    connection = psycopg2.connect(host="192.168.1.13", database="pi", user="postgres", password="Norbi2009")
    cursor = connection.cursor()
    cursor.execute('SELECT registers.address, registers.measurement, registers.dataunit, registers.datatype, registers.functioncode FROM registers '
                   'INNER JOIN energy_meters USING(energy_meter_id) '
                   'WHERE energy_meters.host = \'192.168.1.20\';')
    data = cursor.fetchall()
    for i in data:
        print(i)

def get_config(filename, section):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
       params = parser.items(section)
       for param in params:
           db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


def psql_coonect():
    psql_client = None
    try:
        params = get_config('databases.ini', 'psql')
        psql_client = psycopg2.connect(**params)
        cursor = psql_client.cursor()
        cursor.execute('SELECT version();')
        print('PSQL version: ' + str(cursor.fetchone()))
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as err:
        print(err)
    finally:
        if psql_client is not None:
            psql_client.close()
            print('Connection closed...')

def influx_coonect():
    influx_client = None
    try:
        params = get_config('databases.ini', 'influx')
        influx_client = InfluxDBClient(**params, timeout=5)
        influx_client.request(url='debug/requests')
        print('Succes!')
    except (Exception, ConnectionError) as err:
        print(err)
    finally:
        if influx_client is not None:
            influx_client.close()
            print('Connection closed...')


# psql()
modbus()
# psql_coonect()
# influx_coonect()
