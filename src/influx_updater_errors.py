#!/usr/bin/python3


class ModbusClientException(Exception):
    pass

class UnknownDatatypeException(ModbusClientException):
    pass

class ReadError(ModbusClientException):
    pass

class FunctioncodeException(ModbusClientException):
    pass


class ParserException(Exception):
    pass

class InfluxError(Exception):
    pass