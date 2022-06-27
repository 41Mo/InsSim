#%%
import math

import matplotlib
from modules.libnav.interface.interface import NavIface
import pandas as pd
import numpy as np
from numpy.random import normal as rndnorm
from numpy import array, matrix, linalg, ndarray, newaxis, squeeze
#%matplotlib widget
import matplotlib.pyplot as plt
from src.analysis import rad2me as rad2meters
from src.analysis import c_enu_body, rad2min

df = pd.read_csv('csv_data/Sensors_and_orientation.csv', delimiter=';',skiprows=12)
#df = pd.read_csv('binary_output/logs3/bins-2.csv', delimiter=';',skiprows=12)
#df = pd.read_csv('binary_output/logs3/1.csv', delimiter=';',skiprows=12)
#df = pd.read_csv('binary_output/logs3/t1.csv', delimiter=';',skiprows=12)

#%%
#df.plot( y=["Acc_X"], grid=True, linewidth=2)
acc = df.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
gyr = df.loc[:, ["Gyr_X", "Gyr_Y", "Gyr_Z"]].to_numpy()

#%%
lat = math.radians(55.7522200)
lon = math.radians(37.6155600)
freq = 100
alignemnt_points = 180*freq
gnss_std = math.radians(3/111111)/math.sqrt(1/freq)
gnss_T = 40
gnss_OFF = 10*60
gnss_ON = (gnss_OFF+ 4*60)
gnss_OFF *= freq
gnss_ON *= freq
test_mid_off = True 
acc_offset = np.array([[2*1e-3*9.8, 2*1e-3*9.8, 0*1e-3*9.8]])
gyr_drift = np.array([[math.radians(6)/3600, math.radians(6)/3600, math.radians(0)/3600]])


try:
    yaw = np.arctan2(df["Mag_X"],df["Mag_Y"])
except KeyError:
    try:
        yaw = df["Yaw"].to_numpy()
    except KeyError:
        yaw=0
try:
    mag_yaw = np.mean(yaw[:alignemnt_points])
except TypeError:
    mag_yaw = 0

#%%
if mag_yaw < 0:
    mag_heading = mag_yaw + 2*math.pi
else:
    mag_heading = mag_yaw
points = len(acc)

#%%
time_min = len(acc[:,0])/freq/60
align,acc = np.split(acc, [alignemnt_points])
gyr = np.split(gyr, [alignemnt_points])[1]



gnss = rndnorm((lat, lon), gnss_std, size=(len(acc[:,0]), 2)),
gnss = np.squeeze(gnss)
#gnss = np.array([[lat, lon]]*np.shape(acc)[0])
#%%
ni = NavIface(lat, lon, freq)
ni.nav().alignment_acc(
    np.mean(align[:,0]),
    np.mean(align[:,1]),
    np.mean(align[:,2]),
    mag_heading
)
ini_pry = ni.nav().align_prh()
s=''
s+=f"Kurs: {np.rad2deg(ini_pry[2]+2*np.pi):5.4f}\n"
s+=f"Kren: {np.rad2deg(ini_pry[1]):5.4f}\n"
s+=f"Tangazh: {np.rad2deg(ini_pry[0]):5.4f}\n"
print(s)
#%%
acc = acc - np.mean(acc, axis=0)
gyr = gyr - np.mean(gyr, axis=0)
G=ni.G()
U=ni.U()
# задание начальных условий

# расчет матрицы перехода
C = c_enu_body(ini_pry[2], ini_pry[1], ini_pry[0])

# перепроецируем G из body->enu
a_enu = np.array([
    [0, 0, G]
])
a_body = (C@a_enu.transpose()).transpose()

# перепроецируем W земли из body->enu
w_enu = np.array([
    [0, U*math.cos(lat), U*math.sin(lat)]
])
w_body = (C@w_enu.transpose()).transpose()
acc = acc + a_body + acc_offset
gyr = gyr + w_enu + gyr_drift
#%%
ni.nav().gnss_T(gnss_T)
ni.nav().corr_mode(True)
#%%
pry = []; vel = []; pos = []
i=0
for a, g, sns in zip(acc, gyr, gnss):
    if i == gnss_OFF and test_mid_off:
        ni.nav().corr_mode(False)
    elif i == gnss_ON and test_mid_off:
        ni.nav().corr_mode(True)

    ni.nav().iter_gnss(
        a, g, sns
    )
    pry.append(ni.nav().get_pry())
    vel.append(ni.nav().get_vel())
    pos.append(ni.nav().get_pos())
    i+=1
#%%
def pry2prh(pry):
    if pry[2] < 0:
        pry[2] += 2*math.pi
    return pry

#%%
pos = [np.array(p) - np.array([lat,lon]) for p in pos]
pos = np.array([rad2meters(p).squeeze() for p in pos])
pry = np.array(pry) - np.array(ini_pry)
#pry = [pry2prh(e) for e in pry]
pry = rad2min(pry)
vel = np.array(vel)
#pos = np.rad2deg(pos)
#%%
df2 = pd.DataFrame(
    {
        "Time": np.linspace(alignemnt_points/freq/60, time_min, points-alignemnt_points),
        "Pitch": pry[:,0],
        "Roll": pry[:,1],
        "Hdg": pry[:,2],
        "V_e": vel[:,0],
        "V_n": vel[:,1],
        "Lat": pos[:,0],
        "Lon": pos[:,1]
    }
)
#%%
#30*freq*60
#df2 = df2.iloc[10*60*freq:15*60*freq]
df2 = df2.iloc[gnss_ON+4*gnss_T*freq:]
#df2 = df2.iloc[:gnss_OFF]

#%%
size = (204/25.4, 134.5/25.4) # plot size 140, 170 mm
# To get a list of all of the styles available from Mathplotlib use the following command.
# plt.style.available
#%matplotlib widget
plt.style.use('seaborn-white')
dpi=1000
plt_name = "гнсс полунатур "
df2.plot(
    x="Time", y=["Pitch", "Roll"],
    grid=True,
    figsize=size,
    title=False,
    xlabel="Время, мин",
    ylabel="Угловые минуты",
    sharex=True,
    subplots=True,
    layout=(2,1),
    label=['$\\theta$', '$\gamma$'],
)
# plt.savefig(f"images/{plt_name+'1'}.jpg",dpi=dpi)
# %%
df2.plot(
    x="Time", y=["V_e", "V_n"],
    grid=True,
    figsize=size,
    title=False,
    #title="Cкорости",
    xlabel="Время, мин",
    ylabel="М/с",
    sharex=True,
    subplots=True,
    layout=(2,1),
    label=['$V_e$', '$V_n$'],
    #xlim=(gnss_ON/60+4*gnss_TIME/60,90),
    #ylim=(-5,5),
)

# plt.savefig(f"images/{plt_name+'2'}.jpg",dpi=dpi)
# %%
df2.plot(
    x="Time", y=["Lat", "Lon"],
    grid=True,
    figsize=size,
    title=False,
    #title="Координаты",
    xlabel="Время, мин",
    ylabel="М",
    sharex=True,
    subplots=True,
    layout=(2,1),
    label=['$\\varphi$', '$\lambda$'],
)

# plt.savefig(f"images/{plt_name+'3'}.jpg",dpi=dpi)
#%%
s=''
s+="%5.4f\n"%np.mean(df2["Pitch"])
s+="%5.4f\n"%np.mean(df2["Roll"])
s+="%5.4f\n"%np.mean(df2["V_e"])
s+="%5.4f\n"%np.mean(df2["V_n"])
s+="%5.4f\n"%np.mean(df2["Lat"])
s+="%5.4f\n"%np.mean(df2["Lon"])
print(s)
# %%
