import numpy as np
from InsSim.algo_base import INS_ALGO
from InsSim.attitude import DCM, skew, wrap_2PI
from InsSim.geoparams.geoparams import geo_param


class Shuler(INS_ALGO):
    '''
    Shuler ins alg
    Body frame convention: y - forward, x- right, z -up
    '''
    def __init__(self):
        self.freq = None
        self.dt = None
        self.alg_name = "SH"
        super().__init__()
    
    def run(self, time):
        from math import sin, cos, tan
        try:
            self.pos0
            self.vel0
            self.att0
        except:
            raise ValueError("initial values not set")
        
        if self.freq == None:
            raise ValueError("Frequency not set")

        nloops = time * self.freq
        dt = self.dt

        result = np.zeros([nloops,3,3])
        result[0] = self.att0, self.vel0, self.pos0 

        dcm_b_e = DCM()
        dcm_b_e.from_euler(self.att0[0], self.att0[1], self.att0[2])
        dcm_b_e : np.matrix = dcm_b_e.matrix

        w_enu = np.zeros(3)
        w_i = np.zeros(3)
        g_n = np.zeros(3)
        A = result[:,0]
        V = result[:,1]
        P = result[:,2]
        for i in range(0,nloops):
            if i == 0:
                result[i] = self.att0, self.vel0, self.pos0
                continue

            rN,rE,G,sp,cp,U = geo_param(P[i-1])
            rN_eff = rN+P[i-1,2]
            rE_eff = rE+P[i-1,2]
            g_n = np.array([0,0,G])
            w_i = np.array([0,U*cp,U*sp])

            a_enu = (dcm_b_e @ self.a[i].reshape((3,1))).A1

            w_enu[0] = -V[i-1,1]/rN_eff
            w_enu[1] = V[i-1,0]/rE_eff + w_i[1]
            w_enu[2] = V[i-1,0]/rE_eff*(sp/cp) + w_i[2]

            V[i] = V[i-1] + (a_enu-g_n)*dt - np.cross(w_enu+w_i,V[i-1])*dt
            V[2] = 0

            dcm_b_e = dcm_b_e + (dcm_b_e @ skew(self.g[i]) - skew(w_enu) @ dcm_b_e )*dt

            p_dot = np.array([
                V[i,1]/rN_eff,
                V[i,0]/rE_eff/cp,
                V[i,2]
            ])
            P[i] = P[i-1] +p_dot*dt

            c0 = np.sqrt(np.power(dcm_b_e[2,0], 2.0) + np.power(dcm_b_e[2,2], 2.0));
            A[i,1] = np.arctan(dcm_b_e[2,1] / c0);
            A[i,0] = -np.arctan2(dcm_b_e[2,0], dcm_b_e[2,2]);
            A[i,2] = np.arctan2(dcm_b_e[0,1], dcm_b_e[1,1]);
        self.results = result
    
    def set_freq(self,freq):
        self.freq = freq
        self.dt = 1/freq

    def get_results(self):
        return self.results

    def error_eq(self, points, bias):
        abx, aby = bias[0,0:2]
        wbx, wby = bias[1,0:2]
        g_enu,sl,cl,U = geo_param(self.pos0)[2:6]
        R = 6378245.0
        return equations(abx, aby, wbx, wby, g_enu, R, points, self.att0[2], self.att0[1])

def equations(daox, daoy, dwox, dwoy, G, R, points, psi, s_teta):
    import math
    from numpy import array, rad2deg
    cos = math.cos; sin = math.sin;
    Phiox = []; Phioy = []; Dvx = []; Dvy = []; Dlamda = []; Dphi = [];
    nu = math.sqrt(G/R)
    for t in range(points):
        Phiox.append(- daoy/G - dwox*sin(nu*t)/nu)
        Phioy.append(daox/G - dwoy*(sin(nu*t)/nu))
        Dvx.append(dwoy*R*(1-cos(nu*t)))
        Dvy.append(-dwox*R*(1-cos(nu*t)))
        Dlamda.append(dwoy*(t-sin(nu*t)/nu))
        Dphi.append(-dwox*(t-sin(nu*t)/nu))

    Phioy = array(Phioy)
    Phiox = array(Phiox)
    theta = rad2deg(-(Phiox*cos(psi) - Phioy*sin(psi)))
    gamma = rad2deg(-(Phioy*cos(psi) + Phiox * sin(psi))*1/cos(s_teta))
    Dphi = rad2deg(array(Dphi))
    Dlamda = rad2deg(array(Dlamda))

    return [gamma, theta], [Dvx, Dvy], [Dphi,Dlamda]