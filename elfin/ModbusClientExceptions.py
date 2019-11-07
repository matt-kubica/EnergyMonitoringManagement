#!/usr/bin/python3


class ModbusClientException(Exception):
    # base class
    pass

class UnknownDatatypeException(ModbusClientException):
    pass

class ReadError(ModbusClientException):
    pass

class FunctioncodeException(ModbusClientException):
    pass