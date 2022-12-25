import numpy as np
class INS_ALGO:
    def __init__(self) -> None:
        self.a = np.array([0.0,0.0,0.0])
        self.g = np.array([0.0,0.0,0.0])
        self.gps_pos = np.array([0.0,0.0,0.0])
        self.mag = np.array([0.0])
        self.pos = np.array([0.0,0.0,0.0])
        self.att = np.array([0.0,0.0,0.0])

    def init_alg(self, pos, att) -> None:
        '''
            Alg initialize function. Calls one time, before alg start.
            Args:
                pos: [lat, lng, alt] - rad, rad, m
                att: [roll, pitch, hdg] - rad, rad, rad
        '''
        raise NotImplementedError()

    def step(self, dt):
        raise NotImplementedError()
    
    def get_pos_enu(self):
        '''
            return position
            in format of [lat, lng, alt]
        '''
        raise NotImplementedError()
    
    def get_attitude(self):
        '''
            return attitude
            in format of [roll, pitch, heading]
        '''
        raise NotImplementedError()
    
    def get_vel_enu(self):
        '''
            return velocity
            in format of [ve, vn, vu]
        '''
        raise NotImplementedError()