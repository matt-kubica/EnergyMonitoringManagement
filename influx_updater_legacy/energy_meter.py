from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from utils import DataTypes, FunctionCodes, EndianOrder
from exceptions import UnknownDatatypeException, UnknownFunctioncodeException, ReadError



class EnergyMeter():

    def __init__(self, id, type, description, modbus_client):
        self.id = id
        self.type = type
        self.description = description
        self.modbus_client = modbus_client

    def __eq__(self, other):
        # don't allow comparing other types
        if not isinstance(other, EnergyMeter):
            return NotImplemented
        return self.id == other.id

    def __str__(self):
        return '{0} -> {1}'.format(self.description, self.modbus_client.__str__())

    def __hash__(self):
        return hash(str(self))



class ModbusClient(ModbusTcpClient):

    def __init__(self, host, port, slave_address):
        self.host = host
        self.port = port
        self.slave_address = slave_address
        ModbusTcpClient.__init__(self, host=host, port=port)
        if not self.connect():
            raise ConnectionError('Cannot connect to {0}:{1}'.format(host, port))

    def __str__(self):
        return '{0}:{1}:{2}'.format(self.host, self.port, self.slave_address)


    def get_value(self, register_address, function_code, data_type, word_order, byte_order):
        response = None
        count = None

        if data_type in (DataTypes.LONG, DataTypes.FLOAT):
            count = 2
        elif data_type in (DataTypes.INT, ):
            count = 1
        else:
            raise UnknownDatatypeException('Unknown data type: {0}'.format(data_type))

        if function_code == FunctionCodes.READ_INPUT_REGISTERS:
            response = self.read_input_registers(address=register_address, count=count, unit=self.slave_address)
        elif function_code == FunctionCodes.READ_HOLDING_REGISTERS:
            response = self.read_holding_registers(address=register_address, count=count, unit=self.slave_address)
        else:
            raise UnknownFunctioncodeException('Unknown function code: {0}'.format(function_code))

        if response.isError():
            raise ReadError('Cannot get value from register: {0}, slave_address: {1}'.format(register_address, self.slave_address))

        
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers, 
            byteorder=(Endian.Big if byte_order == EndianOrder.BIG else Endian.Little), 
            wordorder=(Endian.Big if word_order == EndianOrder.BIG else Endian.Little))

        if data_type == DataTypes.FLOAT:
            return decoder.decode_32bit_float()
        elif data_type == DataTypes.LONG:
            return decoder.decode_32bit_int()
        elif data_type == DataTypes.INT:
            return decoder.decode_16bit_int()



class Register():

    def __init__(self, type, register_address, measurement_name, data_unit, data_type, function_code, word_order, byte_order):
        self.type = type
        self.register_address = register_address
        self.measurement_name = measurement_name
        self.data_unit = data_unit
        self.data_type = data_type
        self.function_code = function_code
        self.word_order = word_order
        self.byte_order = byte_order

