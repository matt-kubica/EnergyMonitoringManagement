# EnergyMonitoringManagement
Solution for monitoring energy meters and invertes compatibile with modbusTCP. Based on Python, PostgreSQL, InfluxDB and Grafana.

## Credentials
Credentials for managing postgres, influx and grafana are stored in `.dev.env` file. It's necessary to change usernames and 
passwords in order to keep system secure. Also frequency of readings can be managed via crontab-format env variables.


## Instalation
Since project consist of Docker images that are able to run together via docker-compose, 
only requirement is Docker and docker-compose. 

Installing and running:
```bash
docker-compose up --build -d
```

Monitoring logs:
```bash
docker-compose logs -f
```

Starting:
```bash
docker-compose start 
```

Stopping:
```bash
docker-compose stop 
```

## Configuration
Information about devices (energy_meters) and registers are stored in PostgreSQL database that can be managed via any 
postgres client. By default, database comes with predefined virtual modbustcp server record and its register. Virtual modbustcp server
is another container running in docker-compose which provides random data and helps test behaviour of the system when any other
physical meter is not yet connected. Feel free to delete that records if not needed.

### Structure of tables in database

Energy meters:
| host | port | slave_address | type | description |
| ---- | ---- | ------------- | ---- | ----------- |
| virtual_modbustcp_server | 502 | 0 | virtual_modbustcp | test_energy_meter |

Registers:
| type | register_address | measurement_name | data_unit | data_type | function_code |
| ---- | ---------------- | ---------------- | --------- | --------- | ------------- |
| virtual_modbustcp | 0 | test_measurement | test_u | 1 | 3 |



**NOTE**
* registers table represents register mapping that should be available in datasheet of modbusTCP device
* `host` can be saved as string or ip address
* `description` is helper field (can be null) that figures later on in measurement tags in influxDB
* `type` column of `energy_meters` table references `type` column of `registers` table.
* `data_type` and `function_code` fields are represtented as ints as follows

| data_type | represtents |
| --------- | ----------- |
| 1 | int |
| 2 | long | 
| 3 | float |


| function_code | represtents |
| ------------- | ----------- |
| 3 | READ_HOLDING_REGISTERS |
| 4 | READ_INPUT_REGISTERS |


## Accessing data
After providing energy meter's and register's info, system will periodically (according to crontab config) request values
from all devices and will save them as measurements in influxDB. Then measurements are accessible via grafana (after providing data source)
and allow creating cool graphs :)

