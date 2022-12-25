#%%
import numpy as np

dt = 1

wbx =0; wby =0; wbz =0;
wox = 0; woy = 0.000726; woz=0;

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

C = np.eye(3, 3)

C = C + (C @ w_body  - w_enu @ C) * dt
#%%
from src.sens_data_gen import data_gen
import sys
import matplotlib
import numpy as np
import math as math

from numpy import deg2rad, mean

from modules.libnav.interface.interface import Nav, NavIface, Tarr2d, Tarr3d, Tarr2f, Tarr3f
from src.plots import plot_err_formula, plots
from src.sens_data_gen import data_gen
from src.filter import filter
from src.analysis import c_enu_body, rad2meters, rad2min
from numpy.random import normal as rndnorm
import pandas as pd
import matplotlib.pyplot as plt
import math as m
"""
    Config section
"""
# e.g Moscow 55.7522200 37.6155600
lat = math.radians(55.7522200) # phi
lon = math.radians(37.6155600) # lambda
ini_pos = [lat, lon]
# file with real sensors data
sample_time = 30*60 # seconds
data_frequency = 100 # Hz
save_plots = False # plots would be saved to images folder
plots_size = (297,210) # plots height,width in mm

## alignment
heading = math.radians(0)
roll = math.radians(0)
pitch = math.radians(0)
ini_pry = [pitch, roll, heading]
# time for alignment in seconds
#alignment_time = 60
## alignment

# sensor errors
acc_offset_x = 0* 1e-3 * 9.8  # [m/s/s]
acc_offset_y = 0* 1e-3 * 9.8 # [m/s/s]
gyr_drift_x =  math.radians(10)/3600 # [rad/s]
gyr_drift_y =  math.radians(10)/3600
# normal distribution param
sigma_a = 0.01 #[m/s/s]
sigma_g = math.radians(0.07) # [rad/s]
gnss_std = m.radians((3/111111)/m.sqrt(1/data_frequency))
Tg = 0.2
Ta = 0.3
gnss_TIME = 43
gnss_OFF = 10*60
gnss_ON = gnss_OFF+ 5*60
rad_k = 10
ir_k = 10

size = (140/25.4, 170/25.4) # plot size 140, 170 mm
"""
    Config section end
"""

na = NavIface(lat,lon,data_frequency)
G=na.G()
U=na.U()
# задание начальных условий

# расчет матрицы перехода
C = c_enu_body(heading, roll, pitch)

# перепроецируем G из body->enu
a_enu = np.array([
    [0],
    [0],
    [G]
]
)
a_body = C@a_enu
a_x = a_body[0][0];
a_y = a_body[1][0];
a_z = a_body[2][0];

# перепроецируем W земли из body->enu
w_enu = np.array([
    [0],
    [U*math.cos(lat)],
    [U*math.sin(lat)]
]
)
w_body = C@w_enu
w_x = w_body[0][0];
w_y = w_body[1][0];
w_z = w_body[2][0];
D = data_gen(True,
    [acc_offset_x, acc_offset_y],
    [gyr_drift_x, gyr_drift_y],
    [a_x, a_y, a_z],
    [w_x, w_y, w_z],
    sample_time, data_frequency,
    Ta, Tg,
    sigma_a, sigma_g,
    False
    )

df = pd.read_csv('csv_data/Sensors_and_orientation.csv', delimiter=';',skiprows=12)
#df = pd.read_csv('binary_output/logs3/bins-2.csv', delimiter=';',skiprows=12)
#df = pd.read_csv('binary_output/logs3/1.csv', delimiter=';',skiprows=12)
#df = pd.read_csv('binary_output/logs3/t1.csv', delimiter=';',skiprows=12)

df.iloc[:175000].plot( y=["Gyr_X"], grid=True, linewidth=2)
plt.show()
plt.plot(D[3])
#%%
df.mean(axis='index')