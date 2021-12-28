from matplotlib.colors import is_color_like
import numpy as np
import matplotlib.pyplot as plt
from numpy import cos as cos, double
from numpy import sin as sin
from numpy import tan as tan
import math as math
class nav_alg:

    # Earth parameters
    R = 6378245.0; # earth radius [m]
    U = math.radians(15)/3600 # earth speed [rad/sec]
    G = 9.81 # [m/s/s]

    def __init__(self, frequency=1, time=10800, analysis="static"):
        """
            frequency [HZ]
            time [seconds]
        """
        # input
        self.dt = 1/frequency
        self.number_of_points = int(time / self.dt)
        self.analysis_type = analysis

        # default varaiables
        self._H = 0.0 # object height above ground
        self._w_body = np.array([0, 0, 0], dtype=np.double).reshape(3,1) # angle speed body
        self._a_body = np.array([0, 0, 0], dtype=np.double).reshape(3,1) # acceleration body
        self._v_enu  = np.array([0, 0, 0], dtype=np.double).reshape(3,1)         # linear speed enup
        self._coord   = np.array([0,0], dtype=np.double).reshape(2,1)     # lat, lon (phi, lambda)
        self._tm_body_enu    = np.eye(3, dtype=np.double)                        # transformation matrix body - enup
        self.sensor_data = {}

        # local variables
        self._w_enu          = np.array([0,0,0], dtype=np.double).reshape(3,1)         # angle speed enup
        self._a_enu          = np.array([0,0,0], dtype=np.double).reshape(3,1)         # acceleration enup
        self._rph_angles  = np.array([0,0,0], dtype=np.double).reshape(3,1)         # euler angles
        self.a_after_alignment_body = 0.0
        self.w_after_alignment_body = 0.0
        self.is_aligned = False
        self.is_coordinates_set = False
        self._w_body_input = np.array([0, 0, 0], dtype=np.double).reshape(3,1) # user input
        self._a_body_input = np.array([0, 0, 0], dtype=np.double).reshape(3,1) # user input

        # output
        self.spd_e = []
        self.spd_n = []
        self.pitch = []
        self.roll = []
        self.yaw = []
        self.lat = []
        self.lon = []
        self.a_e = []
        self.a_n = []
        self.a_u = []
        self.w_e = []
        self.w_n = []
        self.w_u = []
        self._init_b() 
    def set_a_body(self, ax, ay, az):
        self._a_body_input=np.array([ax, ay, az]).reshape(3,1)

    def set_w_body(self, wx, wy, wz):
        self._w_body_input=np.array([wx, wy, wz]).reshape(3,1)

    def set_coordinates(self, lat, lon):
        self._coord = np.array([np.deg2rad(lat), np.deg2rad(lon)]).reshape(2,1)
        self.is_coordinates_set = True

    def _puasson_equation(self):
        wbx = self._w_body[0]
        wby = self._w_body[1]
        wbz = self._w_body[2]

        wox = self._w_enu[0]
        woy = self._w_enu[1]
        woz = self._w_enu[2]
        C = self._tm_body_enu

        w_body = np.array([
            [   0, -wbz,  wby],
            [ wbz,    0, -wbx],
            [-wby,  wbx,    0]
        ], dtype=np.double)

        w_enu = np.array([
            [   0, -woz,  woy],
            [ woz,    0, -wox],
            [-woy,  wox,    0]
        ], dtype=np.double)

        self._tm_body_enu = C + (C @ w_body  - w_enu @ C) * self.dt

    def _euler_angles(self):
        C = self._tm_body_enu

        C_0 = np.sqrt(pow(C[2,0],2) + pow(C[2,2],2))

        # teta
        self._rph_angles[0] = np.arctan(C[1,2]/C_0)
        # gamma
        self._rph_angles[1] = -np.arctan(C[0,2]/C[2,2])
        # psi
        self._rph_angles[2] = np.arctan(C[1,0]/C[1,1])

    def _acc_body_enu(self):
        # transformation from horisontal vector to veritical vector
        self._a_enu = (self._tm_body_enu@self._a_body)

    def _coordinates(self):
        lin_spd = self._v_enu
        coords = self._coord

        self._coord[0] = coords[0] + (lin_spd[1]/(self.R+self._H))*self.dt
        self._coord[1] = coords[1] + (lin_spd[0]/((self.R+self._H) * cos(coords[0]))) * self.dt

    def _ang_velocity_body_enu(self):
        spd = self._v_enu
        coord = self._coord

        self._w_enu[0] = -spd[1]/(self.R+self._H) # wox <=> we
        self._w_enu[1] = spd[0]/(self.R+self._H) + self.U * cos(coord[0]) # woy <=> wn
        self._w_enu[2] = spd[0]/(self.R+self._H)*tan(coord[0]) + self.U * sin(coord[0]) # woz <=> wup
    
    def _speed(self):
        w = self._w_enu
        a = self._a_enu
        coord = self._coord
        v = self._v_enu
        tmp = w[2,0]
        # v_e
        #self._v_enu[0][0]
        v1 =  v[0] + (a[0] + (self.U*sin(coord[0])+w[2])*v[1] - v[2]*(self.U*cos(coord[0])+w[1]))*self.dt
        # v_n
        #self._v_enu[1][0]
        v2 =  v[1] + (a[1] - (self.U*sin(coord[0])+w[2])*v[0] - v[2] * w[0])*self.dt
        # v_up. Unstable channel cant ve calculated, so assuming 0
        self._v_enu[2] = 0
        #self._v_enu[2] = v[2] + (a[2] + (self.U*cos(coord[1])+w[1])*v[0] - v[1]*w[0] - 9.81)*self.dt
        v[0] = v1
        v[1] = v2
    def calc_output(self):
            # calculate values on each itaration
            self._acc_body_enu()
            self._speed()
            self._coordinates()
            self._ang_velocity_body_enu()
            self._puasson_equation()
            self._euler_angles()

    def calc_and_save(self):
            self.calc_output()

            # store current values
            v_tmp = self._v_enu.copy()
            c_tmp = self._coord.copy()
            ang_tmp = self._rph_angles.copy()
            self.spd_e.append(v_tmp[0])
            self.spd_n.append(v_tmp[1])
            self.lat.append(c_tmp[0])
            self.lon.append(c_tmp[1])
            self.pitch.append(ang_tmp[0])
            self.roll.append(ang_tmp[1])
            self.yaw.append(ang_tmp[2])
            #a_tmp = self._a_enu.copy()
            #self.a_e.append(a_tmp[0])
            #self.a_n.append(a_tmp[1])
            #self.a_u.append(a_tmp[2])

    def prepare_data(self):
        self.spd_e.pop(0)
        self.spd_n.pop(0)
        self.lat.pop(0)
        self.lon.pop(0)
        self.pitch.pop(0)
        self.roll.pop(0)
        self.yaw.pop(0)

    def static_analysis(self):
        for i in range(self.number_of_points):

            self._w_body[0,0] = self._w_body_input[0,0] + \
                self.w_after_alignment_body[0,0]
            self._w_body[1,0] = self._w_body_input[1,0] + \
                self.w_after_alignment_body[1,0]
            self._w_body[2,0] = self._w_body_input[2,0] + \
                self.w_after_alignment_body[2,0]
                           
            self._a_body[0,0] = self._a_body_input[0,0] + \
                self.a_after_alignment_body[0,0]
            self._a_body[1,0] = self._a_body_input[1,0] + \
                self.a_after_alignment_body[1,0]
            self._a_body[2,0] = self._a_body_input[2,0] + \
                self.a_after_alignment_body[2,0]

            self.calc_and_save()
        self.prepare_data()

    def dynamic_analysis_both(self):
        for i in range(0,self.number_of_points):
            self._w_body[0,0] = self.sensor_data["Gyr_X"][i] + \
                self.w_after_alignment_body[0,0]
            self._w_body[1,0] = self.sensor_data["Gyr_Y"][i] + \
                self.w_after_alignment_body[1,0]
            self._w_body[2,0] = self.sensor_data["Gyr_Z"][i] + \
                self.w_after_alignment_body[2,0]
                           
            self._a_body[0,0] = self.sensor_data["Gyr_X"][i] + \
                self.a_after_alignment_body[0,0]
            self._a_body[1,0] = self.sensor_data["Gyr_Y"][i] + \
                self.a_after_alignment_body[1,0]
            self._a_body[2,0] = self.sensor_data["Gyr_Z"][i] + \
                self.a_after_alignment_body[2,0]
            
            self.calc_and_save()
        self.prepare_data()
    
    def dynamic_analysis_gyro(self):
        for i in range(0,self.number_of_points):
            self._w_body[0,0] = self.sensor_data["Gyr_X"][i] + \
                self.w_after_alignment_body[0,0]
            self._w_body[1,0] = self.sensor_data["Gyr_Y"][i] + \
                self.w_after_alignment_body[1,0]
            self._w_body[2,0] = self.sensor_data["Gyr_Z"][i] + \
                self.w_after_alignment_body[2,0]

            self._a_body[0,0] =self.a_after_alignment_body[0,0]
            self._a_body[1,0] = self.a_after_alignment_body[1,0]
            self._a_body[2,0] = self.a_after_alignment_body[2,0]

            self.calc_and_save()
        self.prepare_data()

    def dynamic_analysis_acc(self):
        for i in range(0,self.number_of_points):
            self._a_body[0,0] = self.sensor_data["Acc_X"][i] + \
                self.a_after_alignment_body[0,0]
            self._a_body[1,0] = self.sensor_data["Acc_Y"][i] + \
                self.a_after_alignment_body[0,0]
            self._a_body[2,0] = self.sensor_data["Acc_Z"][i] + \
                self.a_after_alignment_body[0,0]

            self._w_body[0,0] = self.w_after_alignment_body[0,0]
            self._w_body[1,0] = self.w_after_alignment_body[1,0]
            self._w_body[2,0] = self.w_after_alignment_body[2,0]

            self.calc_and_save()
        self.prepare_data()

    def analysis(self): 
        """
            run analysis
        """
        if not self.is_aligned:
            self.alignment()
            print("aligned with ideal matrix")

        if not self.is_coordinates_set:
            print(f"Coordinates not seted up, going with lat: {self._coord[0]}, lon: {self._coord[1]}")

        if self.analysis_type == "static":
            self.static_analysis()
        
        if self.analysis_type == "dynamic_both":
            self.dynamic_analysis_both()

        if self.analysis_type == "dynamic_gyro":
            self.dynamic_analysis_gyro()

        if self.analysis_type == "dynamic_acc":
            self.dynamic_analysis_acc()


    def alignment(self, psi=0, teta=0, gamma=0):
        def alignment_matrix(psi, teta, gamma):
            psi = np.deg2rad(psi)
            teta = np.deg2rad(teta)
            gamma = np.deg2rad(gamma)
            sp = np.sin(psi)
            st = np.sin(teta)
            sg = np.sin(gamma)
            cp = np.cos(psi)
            ct = np.cos(teta)
            cg = np.cos(gamma)

            a11 = cp*cg + sp*st*sg
            a12 = sp*ct
            a13 = cp*sg - sp*st*cg
            a21 = -sp*cg + cp*st*sg
            a22 = cp*ct
            a23 = -sp*sg - cp*st*cg
            a31 = -ct*sg
            a32 = st
            a33 = ct*cg

            # body_enu matrix
            C_body_enu = np.array([
                [a11, a12, a13],
                [a21, a22, a23],
                [a31, a32, a33]
            ])

            # enu to body matrix
            return C_body_enu.transpose(),C_body_enu


        # assuming we are standing steel
        a_enu = np.array([[0],[0],[self.G]])
        w_enu = np.array([
            [0],
            [self.U*math.cos(self._coord[0])],
            [self.U*math.sin(self._coord[0])]]
        )

        C_enu_body,C_body_enu = alignment_matrix(psi, teta, gamma)
        # re-project vect
        self.a_after_alignment_body = C_enu_body @ a_enu
        self.w_after_alignment_body = C_enu_body @ w_enu
        self._tm_body_enu = C_body_enu.copy()
        self.is_aligned = True

    def plots(self, size=(17,9)):
        """
        generate 3 plots 
        - orientation angles
        - speed
        - coordinates
        """
        plt.figure(figsize=size)
        plt.subplot(3 , 1, 1)
        plt.plot(np.linspace(0, len(self.pitch)*self.dt, len(self.pitch)), np.rad2deg(self.pitch), label="roll")
        plt.legend()
        plt.subplot(3 , 1, 2)
        plt.plot(np.linspace(0, len(self.roll)*self.dt, len(self.roll)), np.rad2deg(self.roll), label="pitch")
        plt.legend()
        plt.subplot(3 , 1, 3)
        plt.plot(np.linspace(0, len(self.yaw)*self.dt, len(self.yaw)), np.rad2deg(self.yaw), label="yaw")
        plt.legend()
        plt.show()

        plt.figure(figsize=size)
        plt.subplot(2 , 1, 1)
        plt.plot(np.linspace(0, len(self.spd_e)*self.dt, len(self.spd_e)), self.spd_e, label="v_e")
        plt.legend()
        plt.subplot(2 , 1, 2)
        plt.plot(np.linspace(0, len(self.spd_n)*self.dt, len(self.spd_n)), self.spd_n, label="v_n")
        plt.legend()
        plt.show()

        plt.figure(figsize=size)
        plt.subplot(2 , 1, 1)
        plt.plot(np.linspace(0, len(self.lat)*self.dt, len(self.lat)), np.rad2deg(self.lat), label="lat")
        plt.legend()
        plt.subplot(2 , 1, 2)
        plt.plot(np.linspace(0, len(self.lon)*self.dt, len(self.lon)), np.rad2deg(self.lon), label="lon")
        plt.legend()
        plt.show()


        #plt.figure(figsize=size)
        #plt.subplot(3 , 1, 1)
        #plt.plot(range(len(self.a_e)), self.a_e, label="a_e")
        #plt.legend()
        #plt.subplot(3 , 1, 2)
        #plt.plot(range(len(self.a_n)), self.a_n, label="a_n")
        #plt.legend()
        #plt.subplot(3 , 1, 3)
        #plt.plot(range(len(self.a_u)), self.a_u, label="a_up")
        #plt.legend()
        #plt.show()

    def _init_b(self):
        la = self._coord[0]
        phi = self._coord[1]
        sl = np.sin(la)
        cl = np.cos(la)
        sp = np.sin(phi)
        cp = np.cos(phi)

        self._b12 = cl
        self._b22 = -sp*sl
        self._b23 = cp
        self._b32 = cp*sl
        self._b33 = sp



class nav_alg_alt(nav_alg):
    def __init__(self, frequency=1, time=10800, analysis="static"):
        nav_alg.__init__(self, frequency, time, analysis)


    def _initial_coordinates(self):
        self._coord[0] = np.arctan(self._b33/self._b23)
        tanphi = np.sqrt( pow(self._b22,2)+pow(self._b32,2) ) / self._b12
        self._coord[1] = np.arctan(tanphi)

    def _ang_velocity(self):
        Vox = self._v_enu[0][0]
        Voy = self._v_enu[1][0]
        self._w_enu[0] = -Voy/self.R
        self._w_enu[1] = self.U * self._b23 + Vox/self.R
        self._w_enu[2] = self.U * self._b33 + Vox/self.R * self._b33/self._b23

    def _speed(self):
        a_e = self._a_enu[0][0]
        a_n = self._a_enu[1][0]
        vx = self._v_enu[0][0]
        vy = self._v_enu[1][0]

        middle = 2*self.U*self._b33 + vx/self.R * self._b33/self._b23

        self._v_enu[0] = a_e*self.dt + middle*vy*self.dt
            #- (2*self.U*self._b23 + self.vx/self.R ) * vz
        self._v_enu[1] = a_n*self.dt + middle*vx*self.dt
    
    def _coordinates(self):
        la = self._coord[0]
        phi = self._coord[1]
        self._coord[0] = phi + self.dt*self._v_enu[1]/(self.R)
        self._coord[1] = la + self.dt*self._v_enu[0]/(self.R*np.cos(phi))

    def _b_coeff(self):
        vox = self._v_enu[0]
        voy = self._v_enu[1]
        uox = -voy / self.R
        uoy = vox / self.R
        uoz = vox/self.R*np.tan(self._coord[1])

        b12 = self._b12
        b22 = self._b22
        b23 = self._b23
        b32 = self._b32
        b33 = self._b33

        self._b12 = b12 + (uoz*b22 - uoy*b32)*self.dt
        self._b22 = b22 - (uoz*b12 + uox*b32)*self.dt
        self._b32 = b32 + (uoy*b12 - uox*b22)*self.dt
        self._b23 = b23 + uox*b33*self.dt
        self._b33 = b33 - uox*b23*self.dt

    def calc_output(self):
            # calculate values on each itaration
            self._acc_body_enu()
            self._speed()
            self._coordinates()
            self._ang_velocity()
            self._puasson_equation()
            self._euler_angles()
            self._b_coeff()