#%%
import numpy as np
import math as math

from numpy import linspace as lp
import matplotlib.pyplot as plt

from src.navapi import navapi
from src.csv_parser import get_data_from_csv
from src.white_noize_gen import gen_white_noize
na = navapi()
#%%
"""
    Config section
"""
G=na.get_G()
U=na.get_U()
# e.g Moscow
lat = 55.75 # phi
lon = 37.61 # lambda

# file with real sensors data
sample_time = 5400 # seconds
data_frequency = 100 # Hz
save_plots = False # plots would be saved to images folder
plots_size = (297,210) # plots height,width in mm

## alignment
yaw = math.radians(180)
roll = math.radians(-2)
pitch = math.radians(2)
# time for alignment in seconds
#alignment_time = 60
## alignment

# sensor errors
acc_offset_x = 0.0005 * 9.8  # [m/s/s] e.g 1 [mg]
acc_offset_y = 0.001 * 9.8 # [m/s/s] e.g 1 [mg]
gyr_drift_x = math.radians(2)/3600 # 2 [deg/hour]
gyr_drift_y = math.radians(2)/3600 # 2 [deg/hour]
# normal distribution param
sigma_a = 0.0005 * 9.8 # mg
sigma_g = math.radians(0.05) # 0.05 [deg/sec] 
"""
    Config section end
"""

na.init(roll,pitch, yaw, lat, lon, sample_time, data_frequency)
C = na.c_body_enu(yaw, roll, pitch)


a_enu = np.array([
    [0],
    [0],
    [G]
]
)
a_body = C@a_enu
a_x = a_body[0];
a_y = a_body[1];
a_z = a_body[2];


w_enu = np.array([
    [0],
    [U*math.cos(lat)],
    [U*math.sin(lat)]
]
)
w_body = C@w_enu
w_x = w_body[0];
w_y = w_body[1];
w_z = w_body[2];


#%%

A_X = gen_white_noize(sigma_a, sample_time, data_frequency)
A_Y = gen_white_noize(sigma_a, sample_time, data_frequency)
A_Z = gen_white_noize(sigma_a, sample_time, data_frequency)
A_X = [a + acc_offset_x+a_x for a in A_X]
A_Y = [a + acc_offset_y+a_y for a in A_Y]
A_Z = [a+a_z for a in A_Z]

x_axis = np.linspace(0, data_frequency, len(A_X))
fig,axs = plt.subplots(3,1,sharex=True,constrained_layout=True)
axs[0].plot(x_axis, A_X)
axs[1].plot(x_axis, A_Y)
axs[2].plot(x_axis, A_Z)
plt.show()


G_X = gen_white_noize(sigma_g, sample_time, data_frequency)
G_Y = gen_white_noize(sigma_g, sample_time, data_frequency)
G_Z = gen_white_noize(sigma_g, sample_time, data_frequency)
G_X = [g+gyr_drift_x+w_x for g in G_X]
G_Y = [g+gyr_drift_y+w_y for g in G_Y]
G_Z = [g+w_z for g in G_Z]

x_axis = np.linspace(0, data_frequency, len(G_X))
fig,axs = plt.subplots(3,1,sharex=True,constrained_layout=True)
axs[0].plot(x_axis, G_X)
axs[1].plot(x_axis, G_Y)
axs[2].plot(x_axis, G_Z)
plt.show()

#%%
G_X = gyr_drift_x+w_x;
G_Y = gyr_drift_y+w_y;
G_Z = w_z;
A_X = acc_offset_x+a_x
A_Y = acc_offset_y+a_y
A_Z = a_z

#%%
na.set_sens_data(A_X, A_Y, A_Z, G_X, G_Y, G_Z)
na.main()

#%%
na.plot_err_formula(acc_offset_x, acc_offset_y, gyr_drift_x, gyr_drift_y, G, 6378245.0, )
#%%
na.plots(na.DATA)
#%%
na.plot_err_model()
#%%
"""
c_roll = hw._rph_angles[1]
c_pitch = hw._rph_angles[0]

#print("Roll: ", c_roll,
# "Pitch", c_pitch,
#)

c_roll_err = abs(c_roll)-abs(math.radians(roll))
c_pitch_err = abs(c_pitch)-abs(math.radians(pitch))

print(
"Model err pitch:", math.degrees(c_pitch_err), "\n",
"Model err roll:", math.degrees(c_roll_err), "\n",
)

abz = G #hw.a_pre[2]
abx = 0 #hw.a_pre[0]
aby = 0 #hw.a_pre[1]
dabz = 0
f_pitch_err = acc_offset_y / math.sqrt(math.pow(G,2) - math.pow(aby,2))
f_roll_err = ((abx * dabz) - (acc_offset_x * abz)) / (pow(abx,2) + pow(abz,2))

print(
"Formula err pitch", math.degrees(f_pitch_err), "\n",
"Formula err pitch", math.degrees(f_roll_err), "\n",
)
print(math.degrees(abs(c_pitch_err) - abs(f_pitch_err)),math.degrees(abs(c_roll_err) - abs(f_roll_err)) )
"""