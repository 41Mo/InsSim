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
    def __init__(self, pos, vel, att, use_prec_geoparm=True):
        '''
            Alg initialize function. Calls one time, before alg start.
            Args:
                att: [roll, pitch, hdg] - rad, rad, rad
                vel: [Ve, Vn, Vu] - m/s, m/s, m/s
                pos: [lat, lng, alt] - rad, rad, m
        '''
        self.freq = None
        self.dt = None
        self.pos0 = pos
        self.vel0 = vel
        self.att0 = att
        if use_prec_geoparm:
            self.G,sl,cl,self.U = geo_param(self.pos0)[2:6]
        super().__init__()
    
    def run(self, time):
        from math import sin, cos, tan
        U = self.U
        R = self.R

        nloops = time * self.freq
        dt = self.dt

        result = np.empty([nloops,3,3])
        result[0] = self.att0, self.vel0, self.pos0 

        dcm_b_e = DCM()
        dcm_b_e.from_euler(self.att0[0], self.att0[1], self.att0[2])
        dcm_b_e : np.matrix = dcm_b_e.matrix

        w_enu = np.array([0,0,0])
        a_enu = np.array([0,0,0])
        A = result[:,0]
        V = result[:,1]
        P = result[:,2]
        for i in range(0,nloops):
            if i == 0:
                result[i] = self.att0, self.vel0, self.pos0
                continue


            a_enu = (dcm_b_e @ self.a[i].reshape((3,1))).A1

            V[i,0] = V[i-1,0] + (a_enu[0])*dt \
                # + (U*sin(self.pos[0]) + self.w_enu[2]) * self.V[1]*dt \
                # - (U*cos(self.pos[0]) + self.w_enu[1]) * self.V[2]*dt
        
            V[i,1] = V[i-1,1] + a_enu[1]*dt \
                # - (U*sin(self.pos[0])+ self.w_enu[2])*self.V[0]*dt \
                # - self.V[2]*self.w_enu[0]*dt
        
            V[i,2] = 0#self.V[2] + a_enu[2]*dt

            ep = R+P[i-1,2]

            w_enu = np.array([
                -V[i,1]/ep,
                V[i,0]/ep+U*cos(P[i-1,0]),
                V[i,2]/ep*tan(P[i-1,0])+U*sin(P[i-1,0])
            ])
        
            dcm_b_e = dcm_b_e + (dcm_b_e @ skew(self.g[i]) - skew(w_enu) @ dcm_b_e )*dt

            P[i,0] = P[i-1,0] + V[i,1]/ep * dt
            P[i,1] = P[i-1,1] + V[i,0]/(ep*cos(P[i,0])) * dt

            c0 = np.sqrt(np.power(dcm_b_e[2,0], 2.0) + np.power(dcm_b_e[2,2], 2.0));
            A[i,1] = np.arctan(dcm_b_e[2,1] / c0);
            A[i,0] = -np.arctan(dcm_b_e[2,0] / dcm_b_e[2,2]);
            A[i,2] = np.arctan2(dcm_b_e[0,1], dcm_b_e[1,1]);
        self.results = result
    
    def set_freq(self,freq):
        self.freq = freq
        self.dt = 1/freq

    def get_results(self):
        return self.results