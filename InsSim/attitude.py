import numpy as np

class DCM:
    '''
        Class implementing basic operation with dcm matrix.
        yxz -> ENU conevention
    '''
    def __init__(self) -> None:
        self.matrix = np.eye(3,3)
    
    # def __mul__(self, rhs):
    #     return self.matrix*rhs
    
    # def __rmul__(self, lhs):
    #     return lhs*self.matrix

    def from_euler(self, roll, pitch, heading):
        sp = np.sin(heading)
        st = np.sin(pitch)
        sg = np.sin(roll)

        cp = np.cos(heading)
        ct = np.cos(pitch)
        cg = np.cos(roll)

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
        self.matrix = np.matrix([
            [a11, a12, a13],
            [a21, a22, a23],
            [a31, a32, a33]
        ])

def skew(x):
    if isinstance(x, np.matrix):
        x = x.A1
    return np.array([[0.0, -x[2], x[1]],
                     [x[2], 0.0, -x[0]],
                     [-x[1], x[0], 0.0]])

def wrap_360(agl):
    res = np.mod(agl, 360)
    if res < 0:
        res+= 360
    return res

def wrap_180(angle):
    res = wrap_360(angle);
    if (res > 180):
        res -= 360;
    return res;

def wrap_2PI(radian):
    res = np.mod(radian, 2*np.pi);
    if (res < 0):
        res += np.pi*2;
    return res;

def wrap_PI(radian):
    res = wrap_2PI(radian);
    if (res > np.pi):
        res -= np.pi*2;

    return res;