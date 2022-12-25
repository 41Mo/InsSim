import math
from numpy import array, rad2deg
def plot_err_formula(daox, daoy, dwox, dwoy, G, R, points, psi, s_teta):
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
    theta = rad2deg(-(Phiox*cos(psi) - Phioy*sin(psi)))*60
    gamma = rad2deg(-(Phioy*cos(psi) + Phiox * sin(psi))*1/cos(s_teta))*60
    Dphi = rad2deg(array(Dphi))*111111
    Dlamda = rad2deg(array(Dlamda))*111111

    return [gamma, theta], [Dvx, Dvy], [Dphi,Dlamda]