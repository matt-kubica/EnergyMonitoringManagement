import logging
import sys
import os

from server import VirtualModbusTCPServer
from inverter import get_power, get_energy_today, get_energy_total

from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian


logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s\t%(filename)s\t%(levelname)s\t%(message)s')
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


class VirtualTLC10000(VirtualModbusTCPServer):

    ''' override '''
    def set_datastore(self):
        FUNCTION_CODE = 0x04
        ADDRESS = 0x00

        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        builder.add_32bit_float(get_power())
        builder.add_32bit_float(get_energy_today())
        builder.add_32bit_float(get_energy_total())

        self.store.setValues(FUNCTION_CODE, ADDRESS, builder.to_registers())
        logger.debug('Data store updated')


if __name__ == '__main__':
    port = int(os.environ.get("VIRTUAL_TLC10000_SERVER_PORT"))
    v = VirtualTLC10000(port)
    logger.debug('Server started on port {0}'.format(port))
    v.start()