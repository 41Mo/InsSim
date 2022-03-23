from ctypes import *
import faulthandler
from typing import Tuple
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from numpy import float64, linspace as lp
from numpy import array as array
import math
faulthandler.enable()

api_so = CDLL("modules/test/lib/libnavapi.so")

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

api_so.Analysis_api_new.restype  = c_void_p
api_so.Analysis_api_new.argtypes = None
api_so.api_init.restype = None
api_so.api_init.argtypes = [
                            c_void_p, c_float,
                            c_float, c_float,
                            c_float, c_float,
                            c_int, c_int
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
class navapi(object):
    def __init__(self):
        self.obj = api_so.Analysis_api_new()

    def init(self, roll,pitch,yaw, lat,lon, time,frequency):
        self.time = time
        self.dt = 1/frequency
        self.points = time*frequency
        api_so.api_init(self.obj, roll,pitch,yaw, lat,lon, time,frequency)

    def loop(self):
        api_so.api_loop(self.obj)

    def get_U(self):
        return api_so.api_get_u()
    def get_G(self):
        return api_so.api_get_g()

    def c_body_enu(self, yaw, roll, pitch):
        psi = math.radians(yaw)
        teta= math.radians(pitch);
        gamma= math.radians(roll);

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
        C_enu_body= array([
            [a11, a12, a13],
            [a21, a22, a23],
            [a31, a32, a33]
        ])

        # enu to body matrix
        return C_enu_body.transpose()

    def main(self):
        self.loop()
        self.DATA = self.get_data()
        self.plots(self.DATA)

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

        if (type(g_x) and type(g_y) and type(g_z)) == list:
            for i, gx_i, gy_i, gz_i in zip(range(0, p), g_x, g_y, g_z):
                g[i].X = gx_i; g[i].Y = gy_i; g[i].Z = gz_i
        elif ((type(g_x) and type(g_y) and type(g_z)) == float or float64):
            for i in range(0, p):
                g[i].X = g_x; g[i].Y = g_y; g[i].Z = g_z
        self.sensors = SENS(p, a, g)
        self.set_sens(self.sensors)


    def set_sens(self, s:SENS):
        api_so.api_set_sens(self.obj, s)

    def get_data(self):
        return api_so.api_get_data(self.obj)

    def plot_errors(self, dax, day, dwx, dwy, G, R):
        cos = math.cos; sin = math.sin;
        Phiox = []; Phioy = []; Dvx = []; Dvy = [];
        nu = math.sqrt(G/R)
        x_axis = lp(0, self.time, self.points)
        for t in x_axis:
            Phiox.append((2*day)/G * cos(nu*t) - day/G - dwx*math.sin(nu*t)/nu)
            Phioy.append(dax/G - dwy*(sin(nu*t)/nu))
            Dvx.append(dwy*R*(1-cos(nu*t)))
            Dvy.append(-dwx*R*(1-cos(nu*t)))
        
        fig,axs = plt.subplots(4,1,sharex=True,constrained_layout=True)
        
        axs[0].plot(x_axis, Phiox, label="roll")
        axs[0].set_ylabel('$\\varphi_y$')
        axs[1].plot(x_axis,  Phioy, label="pitch")
        axs[1].set_ylabel('$\\varphi_x$')
        axs[2].plot(x_axis, Dvx, label="yaw")
        axs[2].set_ylabel('$Vox$')
        axs[3].plot(x_axis, Dvy, label="yaw")
        axs[3].set_ylabel('$Voy$')
        axs[3].set_xlabel("время, с")

    def plots(self, data, size:Tuple=(140,170), save:bool=False, title:str="", additional_plots:bool=False):
        """
        generate 1 plot with 7 subplots
        - orientation angles
        - speed
        - coordinates
        additional debug plots:
        - a_e, a_n, a_up
        - w_e, w_n, w_up
        """

        roll =  data.roll[:self.points]
        pitch = data.pitch[:self.points]
        yaw = data.yaw[:self.points]
        v_e = data.v_e[:self.points]
        v_n = data.v_n[:self.points]
        lat = data.lat[:self.points]
        lon = data.lon[:self.points]



        size = (size[0]/25.4, size[1]/25.4)

        fig,axs = plt.subplots(3,1,sharex=True,constrained_layout=True)
        fig.set_size_inches(size)
        x_axis = lp(0, self.time, self.points)
        axs[0].plot(x_axis, roll, label="roll")
        axs[0].set_ylabel('$\\theta$, угл мин')
        axs[1].plot(x_axis,  pitch, label="pitch")
        axs[1].set_ylabel('$\gamma$, угл мин')
        axs[2].plot(x_axis, yaw, label="yaw")
        axs[2].set_ylabel('$\psi$, угл мин')
        axs[2].set_xlabel("время, с")
        if save:
            plt.savefig("./images/"+"angles"+title+".jpg", bbox_inches='tight')
        plt.show()

        fig,axs = plt.subplots(2,1,sharex=True,constrained_layout=True)
        fig.set_size_inches(size)

        axs[0].plot(x_axis, v_e, label="v_e")
        axs[0].set_ylabel('$V_E$, м/c')
        axs[1].plot(x_axis, v_n, label="v_n")
        axs[1].set_ylabel('$V_N$, м/c')
        axs[1].set_xlabel("время, с")

        if save:
            plt.savefig("./images/"+"speed"+title+".jpg", bbox_inches='tight')
        plt.show()

        fig,axs = plt.subplots(2,1,sharex=True,constrained_layout=True)
        fig.set_size_inches(size)

        axs[0].plot(x_axis, lat,label="lat")
        axs[0].set_ylabel('$\\varphi$, м')
        axs[1].plot(x_axis, lon,label="lon")
        axs[1].set_ylabel('$\lambda$, м')
        axs[1].set_xlabel("время, с")


        if save:
            plt.savefig("./images/"+"coord"+title+".jpg", bbox_inches='tight')
        plt.show()

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
