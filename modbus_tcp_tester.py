from pyModbusTCP.client import ModbusClient as TCPModbusClient
from pyModbusTCP import utils
import sys

class ModbusClientException(Exception):
    pass

class UnknownDatatypeException(ModbusClientException):
    pass

class ReadError(ModbusClientException):
    pass

class FunctioncodeException(ModbusClientException):
    pass

class ModbusClient(TCPModbusClient):

    def __init__(self, host, port, slaveaddress, timeout=1):
        self.__host = host
        self.__port = port
        self.__slaveaddress = slaveaddress
        TCPModbusClient.__init__(self, host=host, port=port, unit_id=slaveaddress, timeout=timeout, auto_open=True)

    def get_host(self):
        return self.__host

    def get_port(self):
        return self.__port

    def get_slaveaddress(self):
        return self.__slaveaddress

    # raises UnknownDatatypeException, ReadError, FunctioncodeException
    def get_register_data(self, address, datatype, functioncode):
        if (datatype == 'float'):
            return self.__read_float(address, functioncode)
        elif (datatype == 'int'):
            return self.__read_int(address, functioncode)
        elif (datatype == 'long'):
            return self.__read_long(address, functioncode)
        else:
            raise UnknownDatatypeException('Unknown datatype: ' + str(datatype))

    def __read_float(self, address, functioncode):
        if (functioncode == 3):
            register = self.read_holding_registers(reg_addr=address, reg_nb=2)
            if register:
                return utils.decode_ieee(utils.word_list_to_long(register)[0])
            else:
                raise ReadError('Error during reading register: ' + str(address))
        elif (functioncode == 4):
            register = self.read_input_registers(reg_addr=address, reg_nb=2)
            if register:
                return  utils.decode_ieee(utils.word_list_to_long(register)[0])
            else:
                raise ReadError('Error during reading register: ' + str(address))
        else:
            raise FunctioncodeException('Undefined functioncode: ' + str(functioncode))

    def __read_int(self, address, functioncode):
        if (functioncode == 3):
            register = self.read_holding_registers(reg_addr=address, reg_nb=1)
            if register:
                return register[0]
            else:
                raise ReadError('Error during reading register: ' + str(address))
        elif (functioncode == 4):
            register = self.read_input_registers(reg_addr=address, reg_nb=1)
            if register:
                return register[0]
            else:
                raise ReadError('Error during reading register: ' + str(address))
        else:
            raise FunctioncodeException('Undefined functioncode: ' + str(functioncode))

    def __read_long(self, address, functioncode):
        if (functioncode == 3):
            register = self.read_holding_registers(reg_addr=address, reg_nb=2)
            if register:
                return utils.word_list_to_long(register)[0]
            else:
                raise ReadError('Error during reading register: ' + str(address))
        elif (functioncode == 4):
            register = self.read_input_registers(reg_addr=address, reg_nb=2)
            if register:
                return utils.word_list_to_long(register)[0]
            else:
                raise ReadError('Error during reading register: ' + str(address))
        else:
            raise FunctioncodeException('Undefined functioncode: ' + str(functioncode))


def main():
	m = ModbusClient(sys.argv[1], sys.argv[2], sys.argv[3])
	while True:
		modbus_address = int(input('Modbus address: '))
		modbus_datatype = input('Datatype (float, int, long): ')
		modbus_functioncode = int(input('Functioncode: '))
		result = None
		try:
			result = m.get_register_data(modbus_address, modbus_datatype, modbus_functioncode)
			print('Result: {0}'.format(result))
		except (ReadError, FunctioncodeException, UnknownDatatypeException) as exc:
			print(exc)
		print('\n')

if __name__ == '__main__':
	main()
		


