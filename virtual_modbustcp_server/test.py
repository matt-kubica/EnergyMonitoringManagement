from server import VirtualModbusTCPServer

from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian


class Test(VirtualModbusTCPServer):

	# override
    def set_datastore(self):
        FUNCTION_CODE = 0x04
        ADDRESS = 0x00

        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        builder.add_32bit_float(4.14)

        self.store.setValues(FUNCTION_CODE, ADDRESS, builder.to_registers())


if __name__ == '__main__':
    t = Test(502)
    t.start()