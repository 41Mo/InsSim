import math
import numpy as np
from ..algo_base import INS_ALGO
from ..imu.imu_model import IMU
from ..attitude import DCM
from ..geoparams.geoparams import geo_param
from .error_equations import plot_err_formula
from numba import njit


D2R = math.pi/180

class INS_SIM:

    def __init__(self, freq, att: np.array, algo: INS_ALGO, imu: IMU = None, dataframe = None):
        '''
        Args:
            freq: [fs_imu, fs_gps, fs_mag], Hz.
                fs_imu: The sample rate of IMU. This is also the sample rate of the simulation.
                fs_gps: The sample rate of GPS.
                fs_mag: not used now. The sample rate of the magnetometer is
                    the same as that of the imu.
            att: [roll, pitch, heading], deg
                simulated imu initial orientation

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

    def error_eq(self, points):
        abx, aby = self.imu._acc_bias[0:2]
        wbx, wby = self.imu._gyro_bias[0:2]
        g_enu,sl,cl,U = geo_param(self.alg.pos0)[2:6]
        return plot_err_formula(abx, aby, wbx, wby, g_enu, self.alg.R, points, self.att[2], self.att[1])

    def result(self, key):
        return np.array(self.output[key])
    
    def generate_imu_motion_data(self, time_sec):
        if not self.imu == None:
            self.imu.set_freq(self.fs[0])
            nloops = time_sec*self.fs[0]
            accel_err = np.empty([nloops, 3])
            gyro_err = np.empty([nloops, 3])
            g_e = np.zeros((3,1))
            w_e = np.zeros((3,1))
            for i in range(nloops):
                g_e[2],sl,cl,U = geo_param(self.alg.pos0)[2:6]
                w_e[1] = U*cl; w_e[2] = U*sl
                a_body = (self.dcm_b_e @ g_e).T.A1
                g_body = (self.dcm_b_e @ w_e).T.A1
                accel_err[i] = self.imu.get_accel_err() + a_body
                gyro_err[i] = self.imu.get_gyro_err() + g_body

            self.alg.a = accel_err
            self.alg.g = gyro_err
            self.output["ACC"] = self.alg.a
            self.output["GYR"] = self.alg.g
    
    def get_results(self):
        keys = ["ATT", "SPD", "POS"]
        for k, i in zip(keys, range(len(keys))):
            self.output[k] = self.alg.get_results()[:,i]


    def run(self, time_sec):
        self.generate_imu_motion_data(time_sec)
        self.alg.run(time_sec)
        self.get_results()
