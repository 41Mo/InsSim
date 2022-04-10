import math
from numpy import array, rad2deg, linspace as lp
import matplotlib.pyplot as plt
#plt.style.use('ggplot')
plt.style.use('Solarize_Light2')
from typing import Tuple

def plot_err_formula(daox, daoy, dwox, dwoy, G, R, time, points, psi, s_teta):
    cos = math.cos; sin = math.sin;
    Phiox = []; Phioy = []; Dvx = []; Dvy = []; Dlamda = []; Dphi = [];
    nu = math.sqrt(G/R)
    x_axis = lp(0, time, points)
    for t in x_axis:
        Phiox.append(- daoy/G - dwox*sin(nu*t)/nu)
        Phioy.append(daox/G - dwoy*(sin(nu*t)/nu))
        Dvx.append(dwoy*R*(1-cos(nu*t)))
        Dvy.append(-dwox*R*(1-cos(nu*t)))
        Dlamda.append(dwoy*(t-sin(nu*t)/nu))
        Dphi.append(-dwox*(t-sin(nu*t)/nu))
    
    size = (140/25.4, 170/25.4)
    fig,axs = plt.subplots(6,1,sharex=True,constrained_layout=True)
    fig.set_size_inches(size)
    Phioy = array(Phioy)
    Phiox = array(Phiox)
    teta = -(Phiox*cos(psi) - Phioy*sin(psi))
    gamma = -(Phioy*cos(psi) + Phiox * sin(psi))*1/cos(s_teta)
    axs[0].plot(x_axis, 60*rad2deg(gamma))
    axs[0].set_ylabel('$\\Delta$$\gamma$, угл мин')
    axs[1].plot(x_axis,  60*rad2deg(teta))
    axs[1].set_ylabel('$\\Delta$$\\vartheta$, угл мин')
    axs[2].plot(x_axis, Dvx)
    axs[2].set_ylabel('$\\Delta$Vox, м/с')
    axs[3].plot(x_axis, Dvy)
    axs[3].set_ylabel('$\\Delta$Voy, м/с')
    axs[4].plot(x_axis, rad2deg(array(Dphi))*60)
    axs[4].set_ylabel('$\\Delta$$\phi$, угл мин')
    axs[5].plot(x_axis, rad2deg(array(Dlamda))*60)
    axs[5].set_ylabel('$\\Delta$$\lambda$, угл мин')
    axs[5].set_xlabel("время, с")


    fig.savefig("./images/"+"По формулам"+".jpg", bbox_inches='tight')

def plots(data, time, points, size:Tuple=(140,170), save:bool=False, title:str="", err:bool=False):
    """
    generate 1 plot with 7 subplots
    - orientation angles
    - speed
    - coordinates
    additional debug plots:
    - a_e, a_n, a_up
    - w_e, w_n, w_up
    """
    roll =  data.roll[:points]
    pitch = data.pitch[:points]
    yaw = data.yaw[:points]
    v_e = data.v_e[:points]
    v_n = data.v_n[:points]
    lat = data.lat[:points]
    lon = data.lon[:points]

    if err:
        pref="$\Delta$"
    else:
        pref=""

    size = (size[0]/25.4, size[1]/25.4)

    fig,axs = plt.subplots(3,1,sharex=True,constrained_layout=True)
    fig.set_size_inches(size)
    x_axis = lp(0, time, points)
    axs[0].plot(x_axis, pitch)
    axs[0].set_ylabel(pref+'$\\theta$, угл мин')
    axs[1].plot(x_axis,  roll)
    axs[1].set_ylabel(pref+'$\gamma$, угл мин')
    axs[2].plot(x_axis, yaw, label="yaw")
    axs[2].set_ylabel(pref+'$\psi$, угл. мин.')
    axs[2].set_xlabel("время, с")
    if save:
        plt.savefig("./images/"+"angles"+title+".jpg", bbox_inches='tight')
    plt.show()

    fig,axs = plt.subplots(2,1,sharex=True,constrained_layout=True)
    fig.set_size_inches(size)

    axs[0].plot(x_axis, v_e)
    axs[0].set_ylabel(pref+'$V_E$, м/c')
    axs[1].plot(x_axis, v_n)
    axs[1].set_ylabel(pref+'$V_N$, м/c')
    axs[1].set_xlabel("время, с")

    if save:
        plt.savefig("./images/"+"speed"+title+".jpg", bbox_inches='tight')
    plt.show()

    fig,axs = plt.subplots(2,1,sharex=True,constrained_layout=True)
    fig.set_size_inches(size)

    axs[0].plot(x_axis, lat,label="lat")
    axs[0].set_ylabel(pref+'$\\varphi$, угл. мин.')
    axs[1].plot(x_axis, lon,label="lon")
    axs[1].set_ylabel(pref+'$\lambda$, угл. мин.')
    axs[1].set_xlabel("время, с")


    if save:
        plt.savefig("./images/"+"coord"+title+".jpg", bbox_inches='tight')
    plt.show()