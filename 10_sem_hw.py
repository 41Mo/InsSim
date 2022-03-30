#%%
import numpy as np
import math as math

from numpy import mean
import matplotlib.pyplot as plt

from src.navapi import navapi, vec_body
from src.csv_parser import get_data_from_csv
from src.white_noize_gen import gen_white_noize
from src.plots import plot_err_formula
na = navapi()
#%%
"""
    Config section
"""
G=na.get_G()
U=na.get_U()
# e.g Moscow
lat = math.radians(55.75) # phi
lon = math.radians(37.61) # lambda

# file with real sensors data
sample_time = 5400 # seconds
data_frequency = 100 # Hz
save_plots = False # plots would be saved to images folder
plots_size = (297,210) # plots height,width in mm

## alignment
yaw = math.radians(0)
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

# задание начальных условий
na.init(lat,lon, sample_time, data_frequency)

# расчет матрицы перехода
C = na.c_enu_body(yaw, roll, pitch)

# перепроецируем G из body->enu
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

# перепроецируем W земли из body->enu
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


#%% генерация массива псевдо реального сигнала, с учетом случайной составляющей

A_X = gen_white_noize(sigma_a, sample_time, data_frequency)
A_Y = gen_white_noize(sigma_a, sample_time, data_frequency)
A_Z = gen_white_noize(sigma_a, sample_time, data_frequency)
A_X = [a + acc_offset_x+a_x for a in A_X]
A_Y = [a + acc_offset_y+a_y for a in A_Y]
A_Z = [a+a_z for a in A_Z]


G_X = gen_white_noize(sigma_g, sample_time, data_frequency)
G_Y = gen_white_noize(sigma_g, sample_time, data_frequency)
G_Z = gen_white_noize(sigma_g, sample_time, data_frequency)
G_X = [g+gyr_drift_x+w_x for g in G_X]
G_Y = [g+gyr_drift_y+w_y for g in G_Y]
G_Z = [g+w_z for g in G_Z]

''' графики случайного сигнала
x_axis = np.linspace(0, data_frequency, len(A_X))
fig1,axs1 = plt.subplots(3,1,sharex=True,constrained_layout=True)
x_axis = np.linspace(0, data_frequency, len(G_X))
fig2,axs2 = plt.subplots(3,1,sharex=True,constrained_layout=True)

axs1[0].plot(x_axis, A_X); axs1[1].plot(x_axis, A_Y); axs1[2].plot(x_axis, A_Z); axs2[0].plot(x_axis, G_X); axs2[1].plot(x_axis, G_Y); axs2[2].plot(x_axis, G_Z)
'''
#%% Сигнал датчиков без учета случайной составляющей
G_X = gyr_drift_x+w_x;
G_Y = gyr_drift_y+w_y;
G_Z = w_z;
A_X = acc_offset_x+a_x
A_Y = acc_offset_y+a_y
A_Z = a_z

#%%
na.alignment_rph(pitch, roll, yaw)
#%% записываем данные в навигационный алгоритм и начинаем расчет
na.set_sens_data(A_X, A_Y, A_Z, G_X, G_Y, G_Z)
na.main()

#%%
d = na.make_err_model() # считаем ошибку
conv = na.convert_data(d) # переводим из си
na.plot_model(conv)
#%% 

#%%
plot_err_formula(
    acc_offset_x,
    acc_offset_y,
    gyr_drift_x,
    gyr_drift_y,
    G,
    6378245.0,
    sample_time,
    sample_time*data_frequency
) 

#%% вычисление ошибок выставки
ae = navapi()
ae.init(lat,lon, sample_time, data_frequency)
ae.alignment_acc(mean(A_X), mean(A_Y), mean(A_Z), yaw) # выставка по значениям акселерометров
res = vec_body()
ae.prh_after_alignment(res)
print(math.degrees(res.X), math.degrees(res.Y), math.degrees(res.Z))
c_roll = res.X; c_pitch = res.Y

# считаем ошибку, относительно значения из условия
c_roll_err = c_roll-roll
c_pitch_err = c_pitch-pitch

print(
"Ошбики при моделировании выставки в угловых минутах:\n",
"по тангажу ", math.degrees(c_pitch_err)*60, "\n",
"по крену ", math.degrees(c_roll_err)*60, "\n",
)

abx = a_body[0] + acc_offset_x
aby = a_body[1] + acc_offset_y
abz = a_body[2]
dabz = 0
f_pitch_err = acc_offset_y / math.sqrt(math.pow(G,2) - math.pow(aby,2))
f_roll_err = ((abx * dabz) - (acc_offset_x * abz)) / (pow(abx,2) + pow(abz,2))

print(
"Ошибка выставки, полученные по формулам в угловых минутах\n",
"по тангажу ", math.degrees(f_pitch_err)*60, "\n",
"по крену", math.degrees(f_roll_err)*60, "\n",
)
print(
"Разница в определении ошибок в угловых минутах\n",
"по тангажу ", math.degrees(c_pitch_err - f_pitch_err)*60, "\n",
"по крену", math.degrees(c_roll_err - f_roll_err)*60
)

# %%
