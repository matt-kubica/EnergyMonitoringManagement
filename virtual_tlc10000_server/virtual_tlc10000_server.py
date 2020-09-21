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
logger.setLevel(logging.INFO)


class VirtualTLC10000(VirtualModbusTCPServer):

    ''' override '''
    def set_datastore(self):
        FUNCTION_CODE = 0x04
        ADDRESS = 0x00

        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        power = get_power()
        energy_today = get_energy_today()
        energy_total = get_energy_total()

        logger.debug('Power = {0}, EnergyToday = {1}, EnergyTotal = {2}'. format(power, energy_today, energy_total))

        builder.add_32bit_float(power)
        builder.add_32bit_float(energy_today)
        builder.add_32bit_float(energy_total)

        self.store.setValues(FUNCTION_CODE, ADDRESS, builder.to_registers())
        logger.info('Data store updated')


if __name__ == '__main__':
    port = int(os.environ.get("VIRTUAL_TLC10000_SERVER_PORT"))
    v = VirtualTLC10000(port)
    logger.info('Server started on port {0}'.format(port))
    v.start()