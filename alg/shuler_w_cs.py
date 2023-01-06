import numpy as np
from InsSim.algo_base import INS_ALGO
from InsSim.attitude import DCM, skew, wrap_2PI
from InsSim.geoparams.geoparams import geo_param, Re, W_IE


class ShulerCLS(INS_ALGO):
    '''
    Shuler ins alg with control loop signals
    Body frame convention: y - forward, x- right, z -up
    '''
    def __init__(self, w_corr=None):
        '''
        w_corr = [w_pos, w_alt, w_hdg] Hz
        '''
        self.freq = None
        self.dt = None
        self.alg_name = "SHCS"
        self.k1 = 0
        self.k2 = 0
        self.k3 = 0
        self.k4 = 0
        self.k5 = 0
        self.k6 = 0
        if isinstance(w_corr, np.ndarray):
            self.setup_mult(w_corr)
        self.prec_geoparam = False
        super().__init__()
    
    def run(self, time):
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

        result = np.zeros([nloops,3,3],dtype=np.float128)
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
        self.dp = []
        for i in range(0,nloops):
            if i == 0:
                result[i] = self.att0, self.vel0, self.pos0
                continue

            if self.prec_geoparam:
                rN,rE,G,sp,cp,U = geo_param(P[i-1])
                rN_eff = rN+P[i-1,2]
                rE_eff = rE+P[i-1,2]
            else:
                rN_eff = Re
                rE_eff = Re
                sp = np.sin(P[i-1,0])
                cp = np.cos(P[i-1,0])
                G=9.81
                U=W_IE
            g_n = np.array([0,0,G])
            w_i = np.array([0,U*cp,U*sp])
            
            delta_pos = P[i-1] - self.gps_pos[i-1]
            self.dp.append(delta_pos)
            delta_hdg = A[i-1,2] - self.comp[i]
            # delta_hdg = 0

            a_enu = (dcm_b_e @ self.a[i].reshape((3,1))).A1

            w_enu[0] = -V[i-1,1]/rN_eff
            w_enu[1] = V[i-1,0]/rE_eff + w_i[1]
            w_enu[2] = V[i-1,0]/rE_eff*(sp/cp) + w_i[2]

            w_enu+=self.omega_signal(delta_pos, delta_hdg, cp)

            V[i] = V[i-1] + (a_enu-g_n)*dt - self.vel_signal(delta_pos, G, cp)*dt - np.cross(w_enu+w_i,V[i-1])*dt
            dcm_b_e = dcm_b_e + (dcm_b_e @ skew(self.g[i]) - skew(w_enu) @ dcm_b_e )*dt

            p_dot = np.array([
                V[i,1]/rN_eff,
                V[i,0]/rE_eff/cp,
                V[i,2]
            ])

            P[i] = P[i-1] + p_dot*dt - self.pos_signal(delta_pos)*dt

            c0 = np.sqrt(np.power(dcm_b_e[2,0], 2.0) + np.power(dcm_b_e[2,2], 2.0))
            A[i,1] = np.arctan(dcm_b_e[2,1] / c0)
            A[i,0] = -np.arctan2(dcm_b_e[2,0], dcm_b_e[2,2])
            A[i,2] = wrap_2PI(np.arctan2(dcm_b_e[0,1], dcm_b_e[1,1]))
        self.results = result
    
    def vel_signal(self, delta_pos, g, cp):
        k = np.array([self.k2, self.k2, self.k5])
        o = np.array([g*cp,g,1])
        d = np.array([delta_pos[1], delta_pos[0], delta_pos[2]])
        return d*k*o

    def omega_signal(self, delta_pos, delta_psi, cp):
        k = np.array([-self.k3, self.k3*cp, -self.k6])
        delta = np.array([delta_pos[0], delta_pos[1], delta_psi])
        return delta*k
    
    def pos_signal(self, delta_pos):
        k = np.array([self.k1, self.k1, self.k4])
        return delta_pos*k
    
    def setup_mult(self, w_corr):
        ws = w_corr[0]
        if ws != 0:
            nu_2 = 1.53804*1e-6
            self.k1 = 1.75*ws
            self.k2 = 2.15*(ws**2)/nu_2 - 1
            self.k3 = (ws**3)/nu_2 - 1.75*ws
        ws = w_corr[1]
        if ws != 0:
            self.k4 = 1.4*ws
            self.k5 = ws**2+2*nu_2
        self.k6 = w_corr[2]
    
    def set_freq(self,freq):
        self.freq = freq
        self.dt = 1/freq

    def get_results(self):
        return self.results