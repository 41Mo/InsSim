import math
import numpy as np
from ..algo_base import INS_ALGO
from ..imu.imu_model import IMU
from ..attitude import DCM
from ..geoparams.geoparams import geo_param
from .error_equations import plot_err_formula


D2R = math.pi/180

class INS_SIM:

    def __init__(self, freq, pos: np.array, att: np.array, algo: INS_ALGO, imu: IMU = None, dataframe = None):
        '''
        Args:
            freq: [fs_imu, fs_gps, fs_mag], Hz.
                fs_imu: The sample rate of IMU. This is also the sample rate of the simulation.
                fs_gps: The sample rate of GPS.
                fs_mag: not used now. The sample rate of the magnetometer is
                    the same as that of the imu.
            pos: [lat, lng, alt]: deg, deg, m AGL
                this is ins initial position
            att: [roll, pitch, heading], deg
                this is ins initial orientation

        '''
        self.fs = freq
        self.alg = algo
        self.imu = imu
        self.dataframe = dataframe
        self.output = {
            "ACC": [],
            "GYR": [],
            "ATT": [],
            "SPD": [],
            "POS": [],
        }

        self.dcm_b_e = DCM()
        self.att = att*D2R
        self.dcm_b_e.from_euler(self.att[0], self.att[1], self.att[2])
        self.dcm_b_e = self.dcm_b_e.matrix

        self.pos = np.array([pos[0]*D2R, pos[1]*D2R, pos[2]])
        self.alg.init_alg(
            self.pos,
            self.att
            )

    def __step(self):
        if not self.imu == None:
            g_enu,sl,cl,U = geo_param(self.pos)[2:6]
            self.alg.a = (self.imu.get_accel_err(1/self.fs[0]) + (self.dcm_b_e * np.matrix([0,0,g_enu]).T).T).A1
            self.alg.g = (self.imu.get_gyro_err(1/self.fs[0]) + (self.dcm_b_e * np.matrix([0,U*cl,U*sl]).T).T).A1

            self.output["ACC"].append(self.alg.a)
            self.output["GYR"].append(self.alg.g)
        self.alg.step(1/self.fs[0])
        self.output["ATT"].append(self.alg.get_attitude())
        self.output["SPD"].append(self.alg.get_vel_enu())
        self.output["POS"].append(self.alg.get_pos_enu())
    
    def error_eq(self, points):
        abx, aby = self.imu._acc_bias[0:2]
        wbx, wby = self.imu._gyro_bias[0:2]
        g_enu,sl,cl,U = geo_param(self.pos)[2:6]
        return plot_err_formula(abx, aby, wbx, wby, g_enu, self.alg.R, points, self.att[2], self.att[1])
    
    def result(self, key):
        return np.array(self.output[key]).squeeze().T
    
    def run(self, time_sec):
        for i in range(0,time_sec*self.fs[0]):
            self.__step()
        
