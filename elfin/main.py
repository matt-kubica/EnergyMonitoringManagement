import Location
import InfluxUpdater
import EnergyMetery
import ModbusClient

from influxdb import InfluxDBClient 

id = 420

influxDBHost                                  = '34.89.239.19'
influxDBPort                                  = '8086'
influxDBName                                  = 'home_energy_monitoring'
influxDBUser                                  = 'admin'
influxDBPass                                  = 'hem_influx_420'

def main():
    new_modbus_client = ModbusClient(host = '192.168.1.30', port = 502, slaveaddress = 1)

    new_energy_meter = EnergyMeter(type = 'sdm630', description = 'main_energy_meter', modbus_client = new_modbus_client)

    new_location = Location(id)
    new_location.add_energy_meter(new_energy_meter)
    locations = []
    locations.append(new_location)

    influx_db_client = InfluxDBClient(host = influxDBHost, port = influxDBPort, username = influxDBUser, password = influxDBPass)
    influx_db_client.switch_database(influxDBName)

    influx_updater = InfluxUpdater(influx_db_client, locations, sqlite_path)
    influx_updater.update_influx()