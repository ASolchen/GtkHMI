
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jason Engman <jengman@testtech-solutions.com>
# Copyright (c) 2021 Adam Solchenberger <asolchenberger@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
from ctypes import c_bool, c_int32, c_int16, c_int64, c_double, c_float
from ctypes import c_int8, c_char, c_uint32, c_uint16, c_uint64, c_uint8


DATATYPES = {
"BOOL": {"Bytes":1, "ModbusRegisters":1, "C_Type": c_bool, "Py_type": bool, 'Py_type_str': 'bool', 'struct_fmt': '?'},
"DINT": {"Bytes":4, "ModbusRegisters":2, "C_Type": c_int32, "Py_type": int, 'Py_type_str': 'int', 'struct_fmt': 'l'},
"INT": {"Bytes":2, "ModbusRegisters":1, "C_Type": c_int16, "Py_type": int, 'Py_type_str': 'int', 'struct_fmt': 'h'},
"LINT": {"Bytes":8, "ModbusRegisters":4, "C_Type": c_int64, "Py_type": int, 'Py_type_str': 'int', 'struct_fmt': 'q'},
"LREAL": {"Bytes":8, "ModbusRegisters":4, "C_Type": c_double, "Py_type": float, 'Py_type_str': 'float', 'struct_fmt': 'd'},
"REAL":	{"Bytes":4, "ModbusRegisters":2, "C_Type": c_float, "Py_type": float, 'Py_type_str': 'float', 'struct_fmt': 'f'},
"SINT":	{"Bytes":1, "ModbusRegisters":1, "C_Type": c_int8, "Py_type": int, 'Py_type_str': 'int', 'struct_fmt': 'b'},
"STRING": {"Bytes":80, "ModbusRegisters":40, "C_Type": c_char * 80, "Py_type": str, 'Py_type_str': 'str', 'struct_fmt': 'c'*80},
"UDINT": {"Bytes":4, "ModbusRegisters":2, "C_Type": c_uint32, "Py_type": int, 'Py_type_str': 'int', 'struct_fmt': 'L'},
"UINT": {"Bytes":2, "ModbusRegisters":1, "C_Type": c_uint16, "Py_type": int, 'Py_type_str': 'int', 'struct_fmt': 'H'},
"ULINT": {"Bytes":8, "ModbusRegisters":4, "C_Type": c_uint64, "Py_type": int, 'Py_type_str': 'int', 'struct_fmt': 'Q'},
"USINT": {"Bytes":1, "ModbusRegisters":1, "C_Type": c_uint8, "Py_type": int, 'Py_type_str': 'int', 'struct_fmt': 'B'}
}