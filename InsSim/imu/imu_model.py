import numpy as np
import math
D2R = math.pi/180

some_model = {
    'accel_b'  : np.array([1* 1e-3 * 9.8, 1* 1e-3 * 9.8, 1* 1e-3 * 9.8]),
    'accel_std': np.array([0.01, 0.01, 0.01]),
    'accel_tau': np.array([0.3, 0.3, 0.3]),
    'gyro_b'   : np.array([0.2, 0.2, 0.2]),
    'gyro_std' : np.array([0.07, 0.07, 0.07]),
    'gyro_tau' : np.array([0.2, 0.2, 0.2]),
}



class IMU:
    def __init__(self, imu_model, gps=None, mag=None):
        '''
        accelerometer:
            accel_b : bias, m/s/s
            accel_std: descrete standard deviation, m/s/s
            accel_tau: correlation T, s

        gyroscopes:
            gyro_b: bias, deg/h
            gyro_std: descrete standart deviation, deg/s
            gyro_tau: correlation T, s
        '''
        if not isinstance(imu_model, dict):
            raise(TypeError)

        imu_model_allowed_keys = [
            'accel_b',
            'accel_std',
            'accel_tau',
            'gyro_b',
            'gyro_std',
            'gyro_tau',
        ]
        
        for k in imu_model.keys():
            if not (k in imu_model_allowed_keys):
                raise(ValueError, f"Unknown key ({k}), given")
            
        for k in imu_model_allowed_keys:
            if not (k in imu_model.keys()):
                raise(ValueError, f"Keys {k}, should be defined")
        
        self._acc_bias = imu_model['accel_b']
        self._acc_std = imu_model['accel_std']
        self._acc_tau = imu_model['accel_tau']

        self._gyro_bias = imu_model['gyro_b']*D2R/3600
        self._gyro_std = imu_model['gyro_std']*D2R
        self._gyro_tau = imu_model['gyro_tau']

        self._accel_w = np.array([0.0,0.0,0.0])
        self._gyro_w = np.array([0.0,0.0,0.0])

    def __non_gaussian_noize(self, std, Tc, prev, dt):
        if Tc == 0:
            return 0.0
        W = (1 - dt/Tc) * prev + std * np.sqrt(2*dt/Tc)*np.random.randn()
    
    def get_accel_err(self, dt) -> np.ndarray:
        noize = []
        for std,tau,w in zip(self._acc_std, self._acc_tau, self._accel_w):
            noize.append(
                self.__non_gaussian_noize(std,tau,w, dt)
            )
        noize = np.array(noize)
        self._accel_w = noize
        return self._acc_bias+noize
    
    def get_gyro_err(self, dt):
        noize = []
        for std,tau,w in zip(self._gyro_std, self._gyro_tau, self._gyro_w):
            noize.append(
                self.__non_gaussian_noize(std,tau,w, dt)
            )
        noize = np.array(noize)
        self._gyro_w = noize
        return self._gyro_bias+noize
