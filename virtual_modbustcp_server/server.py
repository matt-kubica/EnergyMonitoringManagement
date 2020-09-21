
import os
import time

from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

from apscheduler.schedulers.background import BackgroundScheduler




class VirtualModbusTCPServer:

    def __init__(self, port):
        self.port = port

        self.block = ModbusSequentialDataBlock.create()
        self.store = ModbusSlaveContext(ir=self.block)
        self.context = ModbusServerContext(slaves=self.store, single=True)

        self.scheduler = BackgroundScheduler()
        params = {
            'hour': os.environ.get("VIRTUAL_SERVER_UPDATE_CRON_HOUR_TRIGGER"),
            'minute': os.environ.get("VIRTUAL_SERVER_UPDATE_CRON_MINUTE_TRIGGER"),
            'second': os.environ.get("VIRTUAL_SERVER_UPDATE_CRON_SECOND_TRIGGER"),
        }
        self.main_job = self.scheduler.add_job(**params, func=self.set_datastore, trigger='cron')
        
        

    def set_datastore(self):
        FUNCTION_CODE = 0x04
        ADDRESS = 0x00

        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        builder.add_32bit_float(3.14)

        self.store.setValues(FUNCTION_CODE, ADDRESS, builder.to_registers())


    def start(self):
        self.scheduler.start()
        StartTcpServer(self.context, address=("0.0.0.0", self.port))

        

    







