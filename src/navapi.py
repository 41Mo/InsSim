from cmath import pi
from ctypes import *
import faulthandler
from numpy import array, float64, rad2deg
import math
from . plots import *
import os.path
import sys

faulthandler.enable()
lib_path = "modules/libnav/lib"
lib_file = "/libnavapi.so"
if not os.path.exists(lib_path+lib_file):
    print("Use make api in "+lib_path+" first.")
    sys.exit()

api_so = CDLL(lib_path+lib_file)

class vec_body(Structure):
        _fields_ = [("X", c_float),
                    ("Y", c_float),
                    ("Z", c_float),
                    ]
class SENS(Structure):
    _fields_ = [("size", c_int),
                ("acc", POINTER(vec_body)),
                ("gyr", POINTER(vec_body)),
                ]
class OUT(Structure):
    _fields_ = [
                ("roll", POINTER(c_float)),
                ("pitch", POINTER(c_float)),
                ("yaw", POINTER(c_float)),
                ("lat", POINTER(c_float)),
                ("lon", POINTER(c_float)),
                ("v_e", POINTER(c_float)),
                ("v_n", POINTER(c_float)),
                ]
class PY_OUT():
    def __init__(self, roll, pitch, yaw, v_e, v_n, lat, lon) -> None:
        self.roll  = roll;
        self.pitch = pitch;
        self.yaw   = yaw;
        self.lat   = lat;
        self.lon   = lon;
        self.v_e   = v_e;
        self.v_n   = v_n;

api_so.Analysis_api_new.restype  = c_void_p
api_so.Analysis_api_new.argtypes = None

api_so.api_init.restype = None
api_so.api_init.argtypes = [
                            c_void_p, 
                            c_float, c_float,
                            c_int, c_int
                            ]
api_so.api_alignment_rph.restype = None
api_so.api_alignment_rph.argtypes = [
    c_void_p,
    c_float, c_float, c_float
]

api_so.api_alignment_acc.restype = None
api_so.api_alignment_acc.argtypes = [
    c_void_p,
    c_float, c_float, c_float, c_float
]

api_so.api_alignment_cos.restype = None
api_so.api_alignment_cos.argtypes = [
    c_void_p,
    c_float, c_float, c_float, c_float, c_float, c_float
]

api_so.api_set_sens.restype = None
api_so.api_set_sens.argtypes = [c_void_p, SENS]

api_so.api_get_data.restype = OUT
api_so.api_get_data.argtypes = [c_void_p]

api_so.api_loop.restype = None
api_so.api_loop.argtypes = [c_void_p]

api_so.api_get_g.restype = c_float
api_so.api_get_g.argtypes = None

api_so.api_get_u.restype = c_float
api_so.api_get_u.argtypes = None

api_so.api_get_prh.restype = None
api_so.api_get_prh.argtypes = [c_void_p, POINTER(vec_body)]

class navapi(object):
    def __init__(self):
        self.obj = api_so.Analysis_api_new()

    def init(self, lat,lon, time,frequency):
        self.time = time
        self.dt = 1/frequency
        self.points = time*frequency
        self.lat = lat; self.lon=lon;
        api_so.api_init(self.obj, lat,lon, time,frequency)

    def loop(self):
        api_so.api_loop(self.obj)

    def get_U(self):
        return api_so.api_get_u()

    def get_G(self):
        return api_so.api_get_g()

    def c_enu_body(self, yaw, roll, pitch):
        psi = yaw
        teta= pitch;
        gamma= roll;

        sp = math.sin(psi)
        st = math.sin(teta)
        sg = math.sin(gamma)

        cp = math.cos(psi)
        ct = math.cos(teta)
        cg = math.cos(gamma)

        a11 = cp*cg + sp*st*sg
        a12 = sp*ct
        a13 = cp*sg - sp*st*cg
        a21 = -sp*cg + cp*st*sg
        a22 = cp*ct
        a23 = -sp*sg - cp*st*cg
        a31 = -ct*sg
        a32 = st
        a33 = ct*cg

        # body_enu matrix
        C_body_enu= array([
            [a11, a12, a13],
            [a21, a22, a23],
            [a31, a32, a33]
        ])

        # enu to body matrix
        return C_body_enu.transpose()

    def main(self):
        self.loop()
        self.DATA = self.get_data()

    def set_sens_data(self, a_x, a_y, a_z, g_x, g_y, g_z):
        '''
        a - accelerometer data
        g - gyroscope data
        '''
        # ctypes magic
        p = self.points
        TypeVecBodyArr = vec_body * p
        a = TypeVecBodyArr()
        g = TypeVecBodyArr()

        #
        if (type(a_x) and type(a_y) and type(a_z)) == list:
            for i, ax_i, ay_i, az_i in zip(range(0, p), a_x, a_y, a_z):
                a[i].X = ax_i; a[i].Y = ay_i; a[i].Z = az_i
        elif ((type(a_x) and type(a_y) and type(a_z)) == float or float64):
            for i in range(0, p):
                a[i].X = a_x; a[i].Y = a_y; a[i].Z = a_z
        else:
            print("Wrong set sens data type. Use float or list instead.")
            sys.exit()

        if (type(g_x) and type(g_y) and type(g_z)) == list:
            for i, gx_i, gy_i, gz_i in zip(range(0, p), g_x, g_y, g_z):
                g[i].X = gx_i; g[i].Y = gy_i; g[i].Z = gz_i
        elif ((type(g_x) and type(g_y) and type(g_z)) == float or float64):
            for i in range(0, p):
                g[i].X = g_x; g[i].Y = g_y; g[i].Z = g_z
        else:
            print("Wrong set sens data type. Use float or list instead.")
            sys.exit()

        self.sensors = SENS(p, a, g)
        self.set_sens(self.sensors)


    def set_sens(self, s:SENS):
        api_so.api_set_sens(self.obj, s)

    def get_data(self):
        return api_so.api_get_data(self.obj)

    def plot_model(self, DATA):
        plots(DATA, self.time, self.points)

    def make_err_model(self):
        d = self.DATA
        FloatArrType = c_float * self.points
        roll = FloatArrType(); pitch = FloatArrType(); yaw = FloatArrType()
        v_e = FloatArrType(); v_n = FloatArrType(); lat = FloatArrType()
        lon = FloatArrType()
        for i in range(0, self.points):
            roll[i] = d.roll[i] - self.roll
            pitch[i] = d.pitch[i] - self.pitch
            yaw[i] = d.yaw[i] - self.yaw
            v_e[i] = d.v_e[i]
            v_n[i] = d.v_n[i]
            lat[i] = d.lat[i] - self.lat
            lon[i] = d.lon[i] - self.lon
        return OUT(roll ,pitch, yaw, lat, lon, v_e, v_n)
    
    def alignment_rph(self, roll, pitch, yaw):
        self.roll = roll; self.pitch = pitch; self.yaw = yaw
        api_so.api_alignment_rph(self.obj, roll, pitch, yaw)
    def alignment_acc(self, ax_mean, ay_mean, az_mean, yaw):
        api_so.api_alignment_acc(self.obj, ax_mean, ay_mean, az_mean, yaw)
    def alignment_cos(self, st, ct, sg, cg, sp, cp):
        api_so.api_alignment_cos(self.obj, st, ct, sg, cg, sp, cp)
    
    def convert_data(self, data):
        '''
            convert data
            angles rad->degrees
            coord rad->meters
        '''
        points = self.points
        roll  = rad2deg(data.roll[:points])
        pitch = rad2deg(data.pitch[:points])
        yaw   = rad2deg(data.yaw[:points])
        v_e   = data.v_e[:points]
        v_n   = data.v_n[:points]
        lat   = rad2deg(data.lat[:points])
        lon   = rad2deg(data.lon[:points])

        d = PY_OUT(roll, pitch, yaw, v_e, v_n, lat, lon)
        return d

    def prh_after_alignment(self, v):
        api_so.api_get_prh(self.obj, v)
''' example
t = navapi()
size = 5
ARR = vec_body * size;
acc_arr = ARR()
gyr_arr = ARR()
for i in range(0,size):
    acc_arr[i] = vec_body(1, 2, 3)
    gyr_arr[i] = vec_body(3, 4, 5)

sens = SENS(size, acc_arr, gyr_arr)

t.init(0, 0, 0, 0, 0, 1, 5)
t.set_sens(sens)
t.loop()
t_o = t.get_data()

for i in range(0, size):
    print(t_o.lat[i])
'''
