import numpy as np
from InsSim.algo_base import INS_ALGO
from InsSim.attitude import DCM, skew, wrap_2PI
from InsSim.geoparams.geoparams import geo_param


class FIA(INS_ALGO):
    '''
    Free intergration
    Body frame convention: y - forward, x- right, z -up
    '''
    R = 6378245.0
    U = 0.0000726
    G = 9.81
    def __init__(self, use_prec_geoparm=True):
        self.use_prec_geoparm = use_prec_geoparm
        super().__init__()
    
    def init_alg(self, pos, att) -> None:
        self.pos = pos
        self.dcm_b_e = DCM()
        self.dcm_b_e.from_euler(att[0], att[1], att[2])
        self.dcm_b_e : np.matrix = self.dcm_b_e.matrix
        self.V = np.array([0,0,0], dtype=np.float64)
        self.w_enu = np.array([0,0,0])
        self.att = np.array([0,0,0])

        if self.use_prec_geoparm:
            self.G,sl,cl,self.U = geo_param(self.pos)[2:6]
    
    def step(self, dt):
        from math import sin, cos, tan
        U = self.U
        R = self.R

        a_enu = (self.dcm_b_e @ self.a.reshape((3,1))).A1

        self.V[0] = self.V[0] + (a_enu[0])*dt \
            # + (U*sin(self.pos[0]) + self.w_enu[2]) * self.V[1]*dt \
            # - (U*cos(self.pos[0]) + self.w_enu[1]) * self.V[2]*dt
        
        self.V[1] = self.V[1] + a_enu[1]*dt \
            # - (U*sin(self.pos[0])+ self.w_enu[2])*self.V[0]*dt \
            # - self.V[2]*self.w_enu[0]*dt
        
        self.V[2] = 0;#self.V[2] + a_enu[2]*dt

        ep = R+self.pos[2]
        self.w_enu = np.array([
            -self.V[1]/ep,
            self.V[0]/ep+U*cos(self.pos[0]),
            self.V[2]/ep*tan(self.pos[0])+U*sin(self.pos[0])
        ])
        
        self.dcm_b_e = self.dcm_b_e + (self.dcm_b_e @ skew(self.g) - skew(self.w_enu) @ self.dcm_b_e )*dt

        self.pos[0] = self.pos[0] + self.V[1]/ep * dt
        self.pos[1] = self.pos[1] + self.V[0]/(ep*cos(self.pos[0])) * dt

    def get_pos_enu(self):
        return self.pos.copy()
    def get_vel_enu(self):
        return self.V.copy()
    def get_attitude(self):
        mat = self.dcm_b_e
        c0 = np.sqrt(np.power(mat[2,0], 2.0) + np.power(mat[2,2], 2.0));
        self.att[1] = np.arctan(mat[2,1] / c0);
        self.att[0] = -np.arctan(mat[2,0] / mat[2,2]);
        self.att[2] = np.arctan2(mat[0,1], mat[1,1]);
        return self.att.copy()

