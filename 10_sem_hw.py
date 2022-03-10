#%%
import numpy as np
import math as math
from importlib import reload
import matplotlib.pyplot as plt

import src.nav_alg
src.nav_alg = reload(src.nav_alg)
from src.nav_alg import nav_alg
from src.csv_parser import get_data_from_csv
from src.white_noize_gen import gen_white_noize

#%%
"""
    Config section
"""
# e.g Moscow
lat = 55.75
lon = 37.61

# file with real sensors data
sample_time = 1800 # seconds
data_frequency = 100 # Hz
save_plots = False # plots would be saved to images folder
plots_size = (297,210) # plots height,width in mm

## alignment
heading = 180
roll = -2
pitch = 2
# time for alignment in seconds
alignment_time = 60
## alignment

# sensor errors
acc_offset_x = 0.001 * 9.8  # [m/s/s] e.g 1 [mg]
acc_offset_y = 0.001 * 9.8# [m/s/s] e.g 1 [mg]
gyr_drift = math.radians(10)/3600 # [deg/hour] e.g. 10 [deg/hour]
# normal distribution param
sigma_a = 0.0005 * 9.8 #mg
frq_a = 3 # hz
"""
    Config section end
"""


hw = nav_alg(frequency=data_frequency, time=sample_time)
hw.set_coordinates(lat, lon)
SENSOR_DATA_ACC = {}
ACC_X = gen_white_noize(sigma_a, sample_time, frq_a)
ACC_Y = gen_white_noize(sigma_a, sample_time, frq_a)
ACC_Z = gen_white_noize(sigma_a, sample_time, frq_a)
ACC_X = [a+acc_offset_x for a in ACC_X]
ACC_Y = [a+acc_offset_y for a in ACC_Y]
ACC_Z = [a for a in ACC_Z]
SENSOR_DATA_ACC.update({ "Acc_X": ACC_X})
SENSOR_DATA_ACC.update({ "Acc_Y": ACC_Y})
SENSOR_DATA_ACC.update({ "Acc_Z": ACC_Z})
hw.sensor_data = SENSOR_DATA_ACC

print(np.mean(ACC_X))


plt.plot(np.linspace(0, data_frequency, len(ACC_X)), ACC_X)
plt.plot(np.linspace(0, data_frequency, len(ACC_Y)), ACC_Y)
plt.plot(np.linspace(0, data_frequency, len(ACC_Z)), ACC_Z)

hw.alignment(True, heading, alignment_time,pitch, roll)
hw._euler_angles()

c_roll = hw._rph_angles[1]
c_pitch = hw._rph_angles[0]

#print("Roll: ", c_roll,
# "Pitch", c_pitch,
#)

c_roll_err = abs(c_roll)-abs(math.radians(roll))
c_pitch_err = abs(c_pitch)-abs(math.radians(pitch))

print(
"Delta pitch:", math.degrees(c_pitch_err), "\n",
"Delta roll:", math.degrees(c_roll_err), "\n",
)

abz = hw.G #hw.a_pre[2]
abx = 0 #hw.a_pre[0]
aby = 0 #hw.a_pre[1]
dabz = 0
f_pitch_err = acc_offset_y / math.sqrt(math.pow(hw.G,2) - math.pow(aby,2))
f_roll_err = ((abx * dabz) - (acc_offset_x * abz)) / (pow(abx,2) + pow(abz,2))

print(
"f_pitch", math.degrees(f_pitch_err), "\n",
"f_roll", math.degrees(f_roll_err), "\n",
)
print(math.degrees(abs(c_pitch_err) - abs(f_pitch_err)),math.degrees(abs(c_roll_err) - abs(f_roll_err)) )