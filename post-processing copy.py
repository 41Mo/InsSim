#%%
import math

import matplotlib
from modules.libnav.interface.interface import NavIface
import pandas as pd
import numpy as np
from numpy.random import normal as rndnorm
#%matplotlib widget
import matplotlib.pyplot as plt
from src.analysis import rad2me as rad2meters

df = pd.read_csv('/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/t2.csv', delimiter=';',skiprows=12)


#%%
#df.plot( y=["Acc_X"], grid=True, linewidth=2)
acc = df.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
gyr = df.loc[:, ["Gyr_X", "Gyr_Y", "Gyr_Z"]].to_numpy()

#%%
lat = math.radians(55.7522200)
lon = math.radians(37.6155600)
freq = 100
alignemnt_points = 120*freq
gnss_std = math.radians(3/111111)/math.sqrt(1/freq)
gnss_T = 15
gnss_OFF = 10*60
gnss_ON = (gnss_OFF+ 5*60)
gnss_OFF *= freq
gnss_ON *= freq
test_mid_off = True
yaw = np.arctan2(df["Mag_X"],df["Mag_Y"])
mag_yaw = np.mean(yaw[:alignemnt_points])
#%%
if mag_yaw < 0:
    mag_heading = mag_yaw + 2*math.pi
else:
    mag_heading = mag_yaw
points = len(acc)

time_min = len(acc[:,0])/freq/60
align,acc = np.split(acc, [alignemnt_points])
gyr = np.split(gyr, [alignemnt_points])[1]


gnss = rndnorm((lat, lon), gnss_std, size=(len(acc[:,0]), 2)),
gnss = np.squeeze(gnss)
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

step = 1
start = 3
stop = 20
GNSS_T = [i for i in range(start,stop+step, step)]
for T in GNSS_T:
    test_alg = NavIface(lat, lon, freq)
    test_alg.nav().alignment_acc(
        np.mean(align[:,0]),
        np.mean(align[:,1]),
        np.mean(align[:,2]),
        mag_heading
    )
    ini_pry = test_alg.nav().align_prh()
    test_alg.nav().gnss_T(T)
    test_alg.nav().corr_mode(True)
    pry = []; vel = []; pos = []
    i=0
    for a, g, sns in zip(acc, gyr, gnss):
        if i == gnss_OFF and test_mid_off:
            test_alg.nav().corr_mode(False)
        elif i == gnss_ON and test_mid_off:
            test_alg.nav().corr_mode(True)

        test_alg.nav().iter_gnss(
            a, g, sns
        )
        pry.append(test_alg.nav().get_pry())
        vel.append(test_alg.nav().get_vel())
        pos.append(test_alg.nav().get_pos())
        i+=1
    pry = np.array(pry)
    pry = np.rad2deg(pry)*60
    s=''
    s+=f"T={T}; Pitch SKO: {np.std((pry[:,0][gnss_ON+4*T*freq:]))}; Roll SKO: {np.std((pry[:,1])[gnss_ON+4*T*freq:])}"
    print(s)



#%%
def pry2prh(pry):
    if pry[2] < 0:
        pry[2] += 2*math.pi
    return pry

#%%
pos = [np.array(p) - np.array([lat,lon]) for p in pos]
pos = np.array([rad2meters(p).squeeze() for p in pos])
pry = np.array(pry) - np.array(ini_pry)
pry = [pry2prh(e) for e in pry]
pry = np.rad2deg(pry)*60
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
df2 = df2.iloc[gnss_ON+4*gnss_T*freq:]
#df2 = df2.iloc[:gnss_OFF]

#%%
size = (140/25.4, 170/25.4)
# To get a list of all of the styles available from Mathplotlib use the following command.
# plt.style.available
#%matplotlib widget
plt.style.use('fivethirtyeight')
df2.plot(
    x="Time", y=["Pitch", "Roll"],
    grid=True,
    figsize=size,
    subplots=True,
    layout=(3,1),
    linewidth=2,
)
# %%
df2.plot(
    x="Time", y=["V_e", "V_n"],
    grid=True,
    figsize=size,
    subplots=True,
    layout=(2,1),
)

# %%
df2.plot(
    x="Time", y=["Lat", "Lon"],
    grid=True,
    figsize=size,
    subplots=True,
    layout=(2,1),
)
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
