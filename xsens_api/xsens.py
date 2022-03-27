#!/bin/python
from ctypes import *

api_so = CDLL("lib/libxsens.so")

class OUT(Structure):
    _fields_ = [
                ("roll", (c_float)),
                ("pitch", (c_float)),
                ("yaw", (c_float)),
                ("lat", (c_float)),
                ("lon", (c_float)),
                ("v_e", (c_float)),
                ("v_n", (c_float)),
                ]

api_so.pyInterface_new.restype = c_void_p
api_so.pyInterface_new.argtypes = [c_float, c_float, c_uint16, c_int64]
api_so.iface_dev_ready.restype = c_bool
api_so.iface_dev_ready.argtypes = [c_void_p]
api_so.iface_get_data.restype = OUT
api_so.iface_get_data.argtypes = [c_void_p]