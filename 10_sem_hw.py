#%%
import numpy as np
import math as math

from numpy import mean, rad2deg
import matplotlib.pyplot as plt

from src.navapi import navapi, vec_body
from src.csv_parser import get_data_from_csv
from src.white_noize_gen import gen_colour_noize
from src.plots import plot_err_formula, plots
na = navapi()
#%%
"""
    Config section
"""
G=na.get_G()
U=na.get_U()
# e.g Moscow
lat = math.radians(0) # phi
lon = math.radians(0) # lambda

# file with real sensors data
corr_mode = True
sample_time = 5400 # seconds
data_frequency = 100 # Hz
corr_time = 10 # period for determining correction factors
save_plots = False # plots would be saved to images folder
plots_size = (297,210) # plots height,width in mm

## alignment
heading = math.radians(0)
roll = math.radians(0)
pitch = math.radians(0)
# time for alignment in seconds
#alignment_time = 60
## alignment

# sensor errors
acc_offset_x = 0.001 * 9.8  # [m/s/s] e.g 1 [mg]
acc_offset_y = 0.002 * 9.8 # [m/s/s] e.g 2 [mg]
gyr_drift_x = math.radians(-2)/3600 # 1 [deg/hour]
gyr_drift_y = math.radians(1)/3600 # 2 [deg/hour]
# normal distribution param
sigma_a = 0.001 * 9.8 # mg
sigma_g = math.radians(0.07) # 0.07 [deg/sec] 
Tg = 0.1
Ta = 0.2
"""
    Config section end
"""

# задание начальных условий
na.init(lat,lon, sample_time, data_frequency, corr_time, corr_mode, roll, pitch, heading)

# расчет матрицы перехода
C = na.c_enu_body(heading, roll, pitch)

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


#%% генерация массивов случайной составляющей
"""
A_X = gen_colour_noize(sigma_a, Ta, sample_time, data_frequency)
A_Y = gen_colour_noize(sigma_a, Ta, sample_time, data_frequency)
A_Z = gen_colour_noize(sigma_a, Ta, sample_time, data_frequency)

G_X = gen_colour_noize(sigma_g, Tg, sample_time, data_frequency)
G_Y = gen_colour_noize(sigma_g, Tg, sample_time, data_frequency)
G_Z = gen_colour_noize(sigma_g, Tg, sample_time, data_frequency)

size = (210/25.4, 297/25.4)
fig1,axs1 = plt.subplots(6,1,constrained_layout=True, sharex='col')
fig1.set_size_inches(size)

# строим автокорреляцию
lags=4
axs1[0,1].set_title("Автокорреляция")
axs1[0,1].acorr(A_X,
    usevlines=False, maxlags=lags, linestyle="solid", marker="");
axs1[1,1].acorr(A_Y,
    usevlines=False, maxlags=lags, linestyle="solid", marker="");
axs1[2,1].acorr(A_Z,
usevlines=False, maxlags=lags, linestyle="solid", marker="");
axs1[3,1].acorr(G_X,
usevlines=False, maxlags=lags, linestyle="solid", marker="");
axs1[4,1].acorr(G_Y,
usevlines=False, maxlags=lags, linestyle="solid", marker="");
axs1[5,1].acorr(G_Z,
usevlines=False, maxlags=lags, linestyle="solid", marker="");

# добавляем к случайному составляющей измеряемое значение и дрейф
A_X = [a + acc_offset_x+a_x for a in A_X]
A_Y = [a + acc_offset_y+a_y for a in A_Y]
A_Z = [a+a_z for a in A_Z]

G_X = [g+gyr_drift_x+w_x for g in G_X]
G_Y = [g+gyr_drift_y+w_y for g in G_Y]
G_Z = [g+w_z for g in G_Z]

#''' графики случайного сигнала
axs1[0].set_title("Сигнал акселерометров")
axs1[3].set_title("Сигнал гироскопов")

x_axis = np.linspace(0, sample_time, len(A_X))

axs1[0].plot(x_axis, A_X)
axs1[0].set_ylabel("x, м/c/c")
axs1[1].plot(x_axis, A_Y)
axs1[1].set_ylabel("y, м/c/c")
axs1[2].plot(x_axis, A_Z)
axs1[2].set_ylabel("z, м/c/c")
axs1[3].plot(x_axis, rad2deg(G_X))
axs1[3].set_ylabel("x, град/c")
axs1[4].plot(x_axis, rad2deg(G_Y))
axs1[4].set_ylabel("y, град/c")
axs1[5].plot(x_axis, rad2deg(G_Z))
axs1[5].set_ylabel("z, град/c")
axs1[5].set_xlabel("время, c");
fig1.savefig("./images/"+"Сигналы датчиков"+".jpg", bbox_inches='tight')

print("X: ", mean(A_X), "\n", "Y:", mean(A_Y), "\n", "Z:", mean(A_Z), "\n",
    "X:", mean(rad2deg(G_X)), "\n", "Y:", mean(rad2deg(G_Y)), "\n", "Z:", mean(rad2deg(G_Z)), "\n")
"""
#'''
#%% Сигнал датчиков без учета случайной составляющей
#"""
G_X = w_x+gyr_drift_x;
G_Y = w_y+gyr_drift_y;
G_Z = w_z
A_X = a_x + acc_offset_x
A_Y = a_y + acc_offset_y
A_Z = a_z
#"""

#%%
na.alignment_acc(mean(A_Y), mean(A_X), mean(A_Z), heading)
res = vec_body()
na.prh_after_alignment(res)
print(math.degrees(res.X), math.degrees(res.Y), math.degrees(res.Z))
# записываем данные в навигационный алгоритм и начинаем расчет
na.set_sens_data(A_X, A_Y, A_Z, G_X, G_Y, G_Z)
na.main()

#%%
#conv = na.convert_data(na.DATA)
#plots(conv, na.time, na.points, title="моделир случ ", save=True)
d = na.make_err_model() # считаем ошибку
conv = na.convert_data(d) # переводим из си
na.plot_model(conv, title="Моделирования случайной ошибки", save=True, err=True)

#%%
acc_offset = np.array([
    [acc_offset_x],
    [acc_offset_y],
    [0]
])
acc_err_body = acc_offset
acc_err_enu = C.transpose() @ acc_err_body 
gyr_drift = np.array([
    [gyr_drift_x],
    [gyr_drift_y],
    [0]
])
gyr_drift_body = gyr_drift
gyr_drift_enu = C.transpose() @ gyr_drift_body
plot_err_formula(
    acc_err_enu[0][0],
    acc_err_enu[1][0],
    gyr_drift_enu[0][0],
    gyr_drift_enu[1][0],
    G,
    6378245.0,
    sample_time,
    sample_time*data_frequency,
    heading,
    pitch
) 

#%% вычисление ошибок выставки
ae = navapi()
ae.init(lat,lon, sample_time, data_frequency)
ae.alignment_acc(mean(A_X), mean(A_Y), mean(A_Z), heading) # выставка по значениям акселерометров
res = vec_body()
ae.prh_after_alignment(res)
print(math.degrees(res.X), math.degrees(res.Y), math.degrees(res.Z))
c_pitch = res.X; c_roll = res.Y

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
