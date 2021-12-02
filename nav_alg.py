import numpy as np
import matplotlib.pyplot as plt
from numpy import cos as cos, double
from numpy import sin as sin
from numpy import tan as tan
class nav_alg:

    # Earth parameters
    R_LAT = 6400000.0; # earth radius [m]
    R_LON = 6400000.0; # earth radius [m]
    U = np.deg2rad(15)/3600 # earth speed [rad/sec]

    def __init__(self, frequency=10, points_count=36000, analysis="static"):
        # input
        self.dt = 1/frequency
        self.number_of_points = points_count
        self.analysis_type = analysis

        # default varaiables
        self._H = 0.0 # object height above ground
        self._w_body = np.array([0, 0, 0], dtype=np.double).reshape(3,1) # angle speed body
        self._a_body = np.array([0, 0, 0], dtype=np.double).reshape(3,1) # acceleration body
        self._v_enu  = np.array([0, 0, 0], dtype=np.double).reshape(3,1)         # linear speed enup
        self.__coordinates   = np.array([0,0], dtype=np.double).reshape(2,1)     # lat, lon
        self._tm_body_enu    = np.eye(3, dtype=np.double)                        # transformation matrix body - enup
        self.sensor_data = {}

        # local variables
        self._w_enu          = np.array([0,0,0], dtype=np.double).reshape(3,1)         # angle speed enup
        self._a_enu          = np.array([0,0,0], dtype=np.double).reshape(3,1)         # acceleration enup
        self.__euler_angles  = np.array([0,0,0], dtype=np.double).reshape(3,1)         # euler angles

        # output
        self.spd_e = []
        self.spd_n = []
        self.pitch = []
        self.roll = []
        self.yaw = []
        self.lat = []
        self.lon = []
        
    def set_a_body(self, ax, ay, az):
        self._a_body=np.array([ax, ay, az]).reshape(3,1)

    def set_w_body(self, wx, wy, wz):
        self._w_body=np.array([wx, wy, wz]).reshape(3,1)

    def set_coordinates(self, lat, lon):
        self.__coordinates = np.array([np.deg2rad(lat), np.deg2rad(lon)]).reshape(2,1)

    def _puasson_equation(self):
        wbx = self._w_body[0]
        wby = self._w_body[1]
        wbz = self._w_body[2]

        wox = self._w_enu[0]
        woy = self._w_enu[1]
        woz = self._w_enu[2]
        C = self._tm_body_enu

        w_body = np.array([
            [   0, -wbz,  wby],
            [ wbz,    0, -wbx],
            [-wby,  wbx,    0]
        ], dtype=np.double)

        w_enu = np.array([
            [   0, -woz,  woy],
            [ woz,    0, -wox],
            [-woy,  wox,    0]
        ], dtype=np.double)

        self._tm_body_enu = C + (C @ w_body  - w_enu @ C)*self.dt

    def _euler_angles(self):
        C = self._tm_body_enu

        C_0 = np.sqrt(pow(C[0,2],2) + pow(C[2,2],2))

        # teta
        self.__euler_angles[0] = np.arctan2(C[1,2],C_0)
        # gamma
        self.__euler_angles[1] = -np.arctan2(C[0,2],C[2,2])
        # psi
        self.__euler_angles[2] = np.arctan2(C[1,0],C[1,1])

    def _acc_body_enu(self):
        # transformation from horisontal vector to veritical vector
        self._a_enu = (self._tm_body_enu@self._a_body)

    def _coordinates(self):
        lin_spd = self._v_enu
        coords = self.__coordinates

        self.__coordinates[0] = coords[0] + (lin_spd[0]/((self.R_LAT+self._H) * cos(coords[1]))) * self.dt
        self.__coordinates[1] = coords[1] + (lin_spd[1]/(self.R_LON+self._H))*self.dt

    def _ang_velocity_body_enu(self):
        spd = self._v_enu
        coord = self.__coordinates

        self._w_enu[0] = -spd[1]/(self.R_LON+self._H) # wox <=> we
        self._w_enu[1] = spd[0]/(self.R_LAT+self._H) + self.U * cos(coord[1]) # woy <=> wn
        self._w_enu[2] = spd[0]/(self.R_LAT+self._H)*tan(coord[1]) + self.U * sin(coord[1]) # woz <=> wup
    
    def _speed(self):
        w = self._w_enu
        a = self._a_enu
        coord = self.__coordinates
        v = self._v_enu
        tmp = w[2,0]
        # v_e
        self._v_enu[0] =  v[0] + (a[0] + (self.U*sin(coord[1])+w[2])*v[1] - v[2]*(self.U*cos(coord[1])+w[1]))*self.dt
        # v_n
        self._v_enu[1] =  v[1] + (a[1] - (self.U*sin(coord[1])+w[2])*v[0] - v[2] * w[0])*self.dt
        # v_up
        self._v_enu[2] = 0
        #self._v_enu[2] = v[2] + (a[2,0] + ())*self.dt

    def calc_output(self):
            # calculate values on each itaration
            self._acc_body_enu()
            self._speed()
            self._coordinates()
            self._ang_velocity_body_enu()
            self._puasson_equation()
            self._euler_angles()

    def calc_and_save(self):
            self.calc_output()

            # store current values
            v_tmp = self._v_enu.copy()
            c_tmp = self.__coordinates.copy()
            ang_tmp = self.__euler_angles.copy()
            self.spd_e.append(v_tmp[0])
            self.spd_n.append(v_tmp[1])
            self.lat.append(c_tmp[0])
            self.lon.append(c_tmp[1])
            self.pitch.append(ang_tmp[0])
            self.roll.append(ang_tmp[1])
            self.yaw.append(ang_tmp[2])

    def prepare_data(self):
        self.spd_e.pop(0)
        self.spd_n.pop(0)
        self.lat.pop(0)
        self.lon.pop(0)
        self.pitch.pop(0)
        self.roll.pop(0)
        self.yaw.pop(0)

    def static_analysis(self):
        for i in range(self.number_of_points):
            self.calc_and_save()
        self.prepare_data()

    def dynamic_analysis_both(self):
        for i in range(self.number_of_points):
            g_x = self.sensor_data["Gyr_X"][i]
            g_y = self.sensor_data["Gyr_Y"][i]
            g_z = self.sensor_data["Gyr_Z"][i]
            a_x = self.sensor_data["Gyr_X"][i]
            a_y = self.sensor_data["Gyr_Y"][i]
            a_z = self.sensor_data["Gyr_Z"][i] 
            self._w_body[0,0] = g_x
            self._w_body[1,0] = g_y
            self._w_body[2,0] = g_z
                           
            self._a_body[0,0] = a_x
            self._a_body[1,0] = a_y
            self._a_body[2,0] = a_z
            
            self.calc_and_save()
        self.prepare_data()
    
    def dynamic_analysis_gyro(self):
        for i in range(self.number_of_points):
            self._w_body[0] = self.sensor_data["Gyr_X"][i],
            self._w_body[1] = self.sensor_data["Gyr_Y"][i],
            self._w_body[2] = self.sensor_data["Gyr_Z"][i],
                           
            self.calc_and_save()
        self.prepare_data()

    def dynamic_analysis_acc(self):
        for i in range(self.number_of_points):
            self._a_body[0] = self.sensor_data["Acc_X"][i],
            self._a_body[1] = self.sensor_data["Acc_Y"][i],
            self._a_body[2] = self.sensor_data["Acc_Z"][i],

            self.calc_and_save()
        self.prepare_data()

    def analysis(self):
        if self.analysis_type == "static":
            self.static_analysis()
        
        if self.analysis_type == "dynamic_both":
            self.dynamic_analysis_both()

        if self.analysis_type == "dynamic_gyro":
            self.dynamic_analysis_gyro()

        if self.analysis_type == "dynamic_acc":
            self.dynamic_analysis_acc()

# plot helper
def plots(obj):
        plt.figure()
        plt.subplot(3 , 1, 1)
        plt.plot(range(len(obj.pitch)), np.rad2deg(obj.pitch), label="roll")
        plt.legend()
        plt.subplot(3 , 1, 2)
        plt.plot(range(len(obj.roll)), np.rad2deg(obj.roll), label="pitch")
        plt.legend()
        plt.subplot(3 , 1, 3)
        plt.plot(range(len(obj.yaw)), np.rad2deg(obj.yaw), label="yaw")
        plt.legend()

        plt.figure()
        plt.subplot(2 , 1, 1)
        plt.plot(range(len(obj.spd_e)), obj.spd_e, label="v_e")
        plt.legend()
        plt.subplot(2 , 1, 2)
        plt.plot(range(len(obj.spd_n)), obj.spd_n, label="v_n")
        plt.legend()

        plt.figure()
        plt.subplot(2 , 1, 1)
        plt.plot(range(len(obj.lat)), np.rad2deg(obj.lat), label="lat")
        plt.legend()
        plt.subplot(2 , 1, 2)
        plt.plot(range(len(obj.lon)), np.rad2deg(obj.lon), label="lon")
        plt.legend()