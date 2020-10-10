# EnergyMonitoringManagement
Solution for monitoring energy meters and invertes compatibile with modbusTCP and also any different (see *Virtual ModbusTCP Server*). Based on Python, PostgreSQL, InfluxDB and Grafana.

## Credentials
Credentials for managing postgres, influx and grafana are stored in environmental variables in `config/.env.dev` file. It's necessary to change usernames and 
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
Information about devices (`energy_meters`) and `registers` are stored in PostgreSQL database that can be managed via any 
postgres client. By default, database comes with predefined virtual modbustcp server record and its register (**bold** in example below). Virtual modbustcp server is another container running in docker-compose which provides random data and helps test behaviour of the system when any other physical meter is not yet connected. Feel free to delete that records if not needed.

### Scheduling 
All energy meters added to database are requested with cron-like schedule as it's predefined in `config/.env.dev`, env variable: `INFLUX_UPDATER_CRON_*_TRIGGER`. Also, script is looking for new added devices every `SCHEDULER_CRON_*_TRIGGER` and it is testing TCP connection with modbusTCP device straight away.

### Database

#### Energy meters:
Adding row to `energy_meters` table equals starting to request newly added energy meter since incoming task execution. 
| id | host | port | slave_address | type | description |
| -- | ---- | ---- | ------------- | ---- | ----------- |
| **0** | **virtual_modbustcp_server** | **502** | **0** | **virtual_modbustcp** | **test_energy_meter** |
| 1 | 192.168.1.113 | 502 | 1 | sdm630 | example |
| 2 | remote_with_open_ports | 8502 | 1 | sdm630 | example | 

#### Registers:
Coressponding registers' mappings have to be configured in table `registers` as follows (column `energy_meters/type` needs to be in *one-to-many* or *many-to-many* relation with `registers/type`):
| type | register_address | measurement_name | data_unit | data_type | function_code | word_order | byte_order |
| ---- | ---------------- | ---------------- | --------- | --------- | ------------- | ---------- | ---------- |
| **virtual_modbustcp** | **0** | **test_measurement** | **test_u** | **1** | **3** | **2** | **2** |
 sdm630          |       0 | voltageL1              | V        | 3    |            4 | 2 | 2 |
 sdm630          |       2 | voltageL2              | V        | 3    |            4 | 2 | 2 |
 sdm630          |       4 | voltageL3              | V        | 3    |            4 | 2 | 2 |
 sdm630          |       6 | currentL1              | A        | 3    |            4 | 2 | 2 |
 sdm630          |       8 | currentL2              | A        | 3    |            4 | 2 | 2 |
 sdm630          |      10 | currentL3              | A        | 3    |            4 | 2 | 2 |
 sdm630          |      52 | activePower            | W        | 3    |            4 | 2 | 2 |

*Only records in bold can be found in preconfigured database, rest is example*.

#### Side notes:
* register mappings should be available in datasheet of modbusTCP device
* `host` can be saved as string or ip address
* `description` is helper field (can be null) that figures later on in measurement tags in influxDB
* `type` column of `energy_meters` table references `type` column of `registers` table.
* `data_type`, `function_code`, `word_order` and `byte_order` fields are represtented as integers as follows:

| `data_type` | represtents |
| ----------- | ----------- |
| 1 | INT |
| 2 | LONG | 
| 3 | FLOAT |


| `function_code` | represtents |
| --------------- | ----------- |
| 3 | READ_HOLDING_REGISTERS |
| 4 | READ_INPUT_REGISTERS |


| `word_order` and `byte_order` | represents |
| ----------------------------- | ---------- |
| 1 | LITTLE_ENDIAN |
| 2 | BIG_ENDIAN |


### Virtual ModbusTCP Server
It is possible to make virtual layer between devices that not support modbusTCP and **EnergyMonitoringManagement**. 
1. Make folder for virtual device, add default `Dockerfile`, `Pipfile` and `server.py` from `virtual_modbustcp_server` directory.
2. Write own script that access data from not compatibile device.
3. Override `VirtualModbusTCPServer().set_datastore()` method as in `virtual_modbutcp_server/test.py`.
4. Add build to `docker-compose.yml`
5. Add new virtual server and register mappings to database.
6. Optionally set different values in `VIRTUAL_SERVER_UPDATE_CRON_*_TRIGGER` to update datastore more or less often.

*Real world example can be found on `production` branch where virtual layer is made for ZeversolarTLC10000*



## Accessing data
Data from requested energy meters can be accesed by InfluxDB API, InfluxDB Client, Grafana, etc...

### InfluxDB API
https://docs.influxdata.com/influxdb/v1.8/tools/api/#influxdb-1-x-http-endpoints

### Grafana
Configuring datasource in grafana allows creating cool graphs very easily, now it can be done by provisioning `config/grafana/datasources/datasource.yml`.
https://grafana.com/docs/grafana/latest/administration/provisioning/

Preconfigured grafana is accesible on port 3000, one example graph ang gauge are available. Dashboards can be provisioned in `config/grafana/dashboards/`.

![Preconfigured grafana](https://i.imgur.com/snvWfxY.png)
