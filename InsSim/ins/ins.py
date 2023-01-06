import math
import numpy as np
from ..algo_base import INS_ALGO
from ..imu.imu_model import IMU
from ..attitude import DCM
from ..geoparams.geoparams import geo_param


D2R = math.pi/180

class INS_SIM:

    def __init__(self, freq, motion_data, algo, imu = None):
        '''
        Args:
            freq: [fs_imu, fs_gps, fs_mag], Hz.
                fs_imu: The sample rate of IMU. This is also the sample rate of the simulation.
                fs_gps: The sample rate of GPS.
                fs_mag: not used now. The sample rate of the magnetometer is
                    the same as that of the imu.
            motion_data:
                [att, vel, pos]
                att: [roll, pitch, hdg] - deg, deg, deg
                vel: [Ve, Vn, Vu] - m/s, m/s, m/s
                pos: [lat, lng, alt] - rad, rad, m
        '''

        if imu == None:
            raise ValueError("Imu not setup properly")

        self.fs = freq
        self.alg_arr = algo
        self.imu = imu
        self.output = {}
        self.motion_data = motion_data
        self.dcm_b_e = DCM()
        self.att = motion_data[0]*D2R
        self.vel = motion_data[1]
        self.pos = motion_data[2]*np.array([D2R, D2R, 1])
        self.dcm_b_e.from_euler(self.att[0], self.att[1], self.att[2])
        self.dcm_b_e = self.dcm_b_e.matrix.T
        self.ini_cond = {
            "ATT":self.att,
            "VEL":self.vel,
            "POS":self.pos
        }

    def result(self, key):
        return np.array(self.output[key])
    
    def generate_imu_values(self, time_sec):
        if self.imu == None:
            raise ValueError
        self.imu.set_freq(self.fs)
        nloops = time_sec*self.fs[0]
        accel_err = np.zeros([nloops, 3])
        gyro_err = np.zeros([nloops, 3])
        g_e = np.zeros((3,1))
        w_e = np.zeros((3,1))

        for i in range(nloops):
            g_e[2],sl,cl,U = geo_param(self.pos)[2:6]
            w_e[1] = U*cl; w_e[2] = U*sl
            a_body = (self.dcm_b_e @ g_e).T.A1
            g_body = (self.dcm_b_e @ w_e).T.A1
            accel_err[i] = self.imu.get_accel_err() + a_body
            gyro_err[i] = self.imu.get_gyro_err() + g_body

        self.output["ACC"] = accel_err
        self.output["GYR"] = gyro_err
    
    def generate_gps_values(self, time_sec):
        if not self.imu.gps_present:
            return
        nloops = time_sec*self.fs[0]
        gps_pos = np.zeros([nloops,3])
        for i in range(nloops):
            gps_pos[i] = self.imu.get_gps_err() + self.pos
        
        self.output["GPS_POS"] = gps_pos

    def generate_compass_values(self, time_sec):
        if not self.imu.compass_present:
            return
        nloops = time_sec*self.fs[0]
        compass = np.zeros(nloops)
        for i in range(nloops):
            compass[i] = self.imu.get_compass_err() + self.att[2]
        
        self.output["COMP"] = compass

    def run(self, time_sec):
        self.generate_imu_values(time_sec)
        self.generate_gps_values(time_sec)
        self.generate_compass_values(time_sec)
        if self.alg_arr == None:
            return
        for alg in self.alg_arr:
            alg.a = self.output["ACC"]
            alg.g = self.output["GYR"]
            alg.comp = self.output.get('COMP')
            alg.gps_pos = self.output.get('GPS_POS')
            alg.att0 = self.att
            alg.vel0 = self.vel
            alg.pos0 = self.pos
            alg.run(time_sec)
            keys = ["ATT", "VEL", "POS"]
            for k, i in zip(keys, range(len(keys))):
                self.output[alg.alg_name+"_"+k] = alg.get_results()[:,i]
                self.output[alg.alg_name+"_"+k+"_ERR"] = alg.get_results()[:,i]-self.ini_cond[k]
