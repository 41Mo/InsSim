import numpy as np
import math
D2R = math.pi/180
M2R = 1/6378245

some_model = {
    'accel_b'  : np.array([1* 1e-3 * 9.8, 1* 1e-3 * 9.8, 1* 1e-3 * 9.8]),
    'accel_std': np.array([0.01, 0.01, 0.01]),
    'accel_tau': np.array([0.3, 0.3, 0.3]),
    'gyro_b'   : np.array([0.2, 0.2, 0.2]),
    'gyro_std' : np.array([0.07, 0.07, 0.07]),
    'gyro_tau' : np.array([0.2, 0.2, 0.2]),
}



class IMU:
    def __init__(self, imu_model, gps=None, compass=None):
        '''
        accelerometer:
            accel_b : bias, m/s/s
            accel_std: descrete standard deviation, m/s/s
            accel_tau: correlation T, s

        gyroscopes:
            gyro_b: bias, deg/h
            gyro_std: descrete standart deviation, deg/s
            gyro_tau: correlation T, s
        gps:
            gps_b: offset, m
            gps_std: stadtard deviation, m
        '''
        if not isinstance(imu_model, dict):
            raise(TypeError)

        imu_model_needed_keys = [
            'accel_b',
            'accel_std',
            'accel_tau',
            'gyro_b',
            'gyro_std',
            'gyro_tau',
        ]

        non_inertial_possible_keys = [
            'gps_b',
            'gps_std',
            'compass_b',
            'compass_std',
        ]
        
        for k in imu_model.keys():
            if not (k in imu_model_needed_keys):
                raise ValueError(f"Unknown key ({k}), given")
            
        for k in imu_model_needed_keys:
            if not (k in imu_model.keys()):
                raise ValueError(f"Keys {k}, should be defined")

        if gps != None:
            for k in gps.keys():
                if not (k in non_inertial_possible_keys):
                    raise ValueError(f"Unknown key ({k}), given")
            b = gps.get('gps_b')
            if isinstance(b, np.ndarray):
                self._gps_b = b * np.array([M2R,M2R,1])
            else:
                self._gps_b = np.zeros(3)
            b = gps.get('gps_std')
            if isinstance(b, np.ndarray):
                self._gps_std = b * np.array([M2R,M2R,1])
            else:
                self._gps_std = np.zeros(3)
            self.gps_present = True
        
        if compass != None:
            for k in compass.keys():
                if not (k in non_inertial_possible_keys):
                    raise ValueError(f"Unknown key ({k}), given")
            b = compass.get('compass_b')
            if b != None:
                self._compass_b = b*D2R
            else:
                self._compass_b = 0
            b = compass.get('compass_std')
            if b != None:
                self._compass_std = b*D2R
            else:
                self._compass_std = 0
            self.compass_present = True

            

        
        self._acc_bias = imu_model['accel_b']
        self._acc_std = imu_model['accel_std']
        self._acc_tau = imu_model['accel_tau']

        self._gyro_bias = imu_model['gyro_b']*D2R/3600
        self._gyro_std = imu_model['gyro_std']*D2R
        self._gyro_tau = imu_model['gyro_tau']

        self._accel_w = np.array([0.0,0.0,0.0])
        self._gyro_w = np.array([0.0,0.0,0.0])

        self._prev_nz_v = np.zeros((2,3))

    def get_accel_err(self) -> np.ndarray:
        self._prev_nz_v[0] = self._acc_t1 * self._prev_nz_v[0] + self._acc_t2*np.random.standard_normal(3)
        return self._acc_bias+self._prev_nz_v[0]
    
    def set_freq(self, freq:np.array) -> None:
        self.dt = 1/freq[0]

        sc :np.ndarray = (self._acc_tau == 0)
        if True in sc:
            raise ValueError(f"accel tau index:{np.where(sc == True)} should not be zero")

        sc :np.ndarray = (self._gyro_tau == 0)
        if True in sc:
            raise ValueError(f"gyro tau index:{np.where(sc == True)} should not be zero")


        self._acc_t1 = (1 - self.dt/self._acc_tau)
        self._acc_t2 = self._acc_std * np.sqrt(2*self.dt/self._acc_tau)

        self._gyro_t1 = (1 - self.dt/self._gyro_tau)
        self._gyro_t2 = self._gyro_std * np.sqrt(2*self.dt/self._gyro_tau)

        self.gps_freq = freq[1]
        self.compass_freq = freq[2]

    
    def get_gyro_err(self) -> np.ndarray:
        self._prev_nz_v[1] = self._gyro_t1 * self._prev_nz_v[1] + self._gyro_t2*np.random.standard_normal(3)
        return self._gyro_bias+self._prev_nz_v[1]

    def get_gps_err(self) -> np.ndarray:
        return self._gps_b + self._gps_std*np.random.standard_normal(3)*math.sqrt(self.gps_freq)
    
    def get_compass_err(self) -> np.ndarray:
        return self._compass_b + self._compass_std*np.random.standard_normal()*math.sqrt(self.compass_freq)