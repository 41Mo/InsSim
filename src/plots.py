import math
from numpy import linspace as lp
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from typing import Tuple

def plot_err_formula(daox, daoy, dwox, dwoy, G, R, time, points):
    cos = math.cos; sin = math.sin;
    Phiox = []; Phioy = []; Dvx = []; Dvy = [];
    nu = math.sqrt(G/R)
    x_axis = lp(0, time, points)
    for t in x_axis:
        Phiox.append((2*daoy)/G * cos(nu*t) - daoy/G - dwox*math.sin(nu*t)/nu)
        Phioy.append(daox/G - dwoy*(sin(nu*t)/nu))
        Dvx.append(dwoy*R*(1-cos(nu*t)))
        Dvy.append(-dwox*R*(1-cos(nu*t)))
    
    fig,axs = plt.subplots(4,1,sharex=True,constrained_layout=True)
    
    axs[0].plot(x_axis, Phiox, label="roll")
    axs[0].set_ylabel('$\\varphi_y$')
    axs[1].plot(x_axis,  Phioy, label="pitch")
    axs[1].set_ylabel('$\\varphi_x$')
    axs[2].plot(x_axis, Dvx, label="yaw")
    axs[2].set_ylabel('$Vox$')
    axs[3].plot(x_axis, Dvy, label="yaw")
    axs[3].set_ylabel('$Voy$')
    axs[3].set_xlabel("время, с")


def plots(data, time, points, size:Tuple=(140,170), save:bool=False, title:str="", additional_plots:bool=False):
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



    size = (size[0]/25.4, size[1]/25.4)

    fig,axs = plt.subplots(3,1,sharex=True,constrained_layout=True)
    fig.set_size_inches(size)
    x_axis = lp(0, time, points)
    axs[0].plot(x_axis, roll, label="roll")
    axs[0].set_ylabel('$\\theta$, угл мин')
    axs[1].plot(x_axis,  pitch, label="pitch")
    axs[1].set_ylabel('$\gamma$, угл мин')
    axs[2].plot(x_axis, yaw, label="yaw")
    axs[2].set_ylabel('$\psi$, угл мин')
    axs[2].set_xlabel("время, с")
    if save:
        plt.savefig("./images/"+"angles"+title+".jpg", bbox_inches='tight')
    plt.show()

    fig,axs = plt.subplots(2,1,sharex=True,constrained_layout=True)
    fig.set_size_inches(size)

    axs[0].plot(x_axis, v_e, label="v_e")
    axs[0].set_ylabel('$V_E$, м/c')
    axs[1].plot(x_axis, v_n, label="v_n")
    axs[1].set_ylabel('$V_N$, м/c')
    axs[1].set_xlabel("время, с")

    if save:
        plt.savefig("./images/"+"speed"+title+".jpg", bbox_inches='tight')
    plt.show()

    fig,axs = plt.subplots(2,1,sharex=True,constrained_layout=True)
    fig.set_size_inches(size)

    axs[0].plot(x_axis, lat,label="lat")
    axs[0].set_ylabel('$\\varphi$, м')
    axs[1].plot(x_axis, lon,label="lon")
    axs[1].set_ylabel('$\lambda$, м')
    axs[1].set_xlabel("время, с")


    if save:
        plt.savefig("./images/"+"coord"+title+".jpg", bbox_inches='tight')
    plt.show()