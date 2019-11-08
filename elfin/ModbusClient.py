#!/usr/bin/python3

from pyModbusTCP.client import ModbusClient as TCPModbusClient
from pyModbusTCP import utils
import ModbusClientExceptions

class ModbusClient(TCPModbusClient):

    def __init__(self, host, port, slaveaddress, timeout = 1):
        TCPModbusClient.__init__(self, host = host, port = port, unit_id = slaveaddress, timeout = timeout, auto_open = True)

    # raises UnknownDatatypeException, ReadError, FunctioncodeException
    def get_register_data(self, address, datatype, functioncode):
        if(datatype == 'float'):
            self._read_float(address, functioncode)
        elif(datatype == 'int'):
            self._read_int(address, functioncode)
        elif(datatype == 'long'):
            self._read_long(address, functioncode)
        else:
            raise UnknownDatatypeException
    
    def _read_float(self, address, functioncode):
        if(functioncode == 3):
            register = self.read_holding_registers(reg_addr = address, reg_nb = 2)
            if register:
                return utils.decode_ieee(utils.word_list_to_long(register))
            else:
                raise ReadError
        elif(functioncode == 4):
            register = self.read_input_registers(reg_addr = address, reg_nb = 2)
            if register:
                return utils.decode_ieee(utils.word_list_to_long(register))
            else:
                raise ReadError
        else:
            raise FunctioncodeException
    
    def _read_int(self, address, functioncode):
        if(functioncode == 3):
            register = self.read_holding_registers(reg_addr = address, reg_nb = 1)
            if register:
                return register[0]
            else:
                raise ReadError
        elif(functioncode == 4):
            register = self.read_input_registers(reg_addr = address, reg_nb = 1)
            if register:
                return register[0]
            else:
                raise ReadError
        else:
            raise FunctioncodeException

    def _read_long(self, address, functioncode):
        if(functioncode == 3):
            register = self.read_holding_registers(reg_addr = address, reg_nb = 2)
            if register:
                return utils.word_list_to_long(register)
            else:
                raise ReadError
        elif(functioncode == 4):
            register = self.read_input_registers(reg_addr = address, reg_nb = 2)
            if register:
                return utils.word_list_to_long(register)
            else:
                raise ReadError
        else:
            raise FunctioncodeException
            
