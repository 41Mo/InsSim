#%%
import numpy as np
import math as math

from numpy import mean

from modules.libnav.interface.interface import NavIface, Tarr2f, Tarr3f
from src.csv_parser import get_data_from_csv
from src.plots import plot_err_formula, plots
from src.sens_data_gen import data_gen
from src.analysis import c_enu_body, rad2meters, rad2min
#%%
"""
    Config section
"""
# e.g Moscow
lat = math.radians(0) # phi
lon = math.radians(0) # lambda

# file with real sensors data
sample_time = 5400 # seconds
data_frequency = 10 # Hz
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
acc_offset_y = 0.002 * 9.8 # [m/s/s] e.g 1 [mg]
gyr_drift_x = math.radians(1)/3600 # 2 [deg/hour]
gyr_drift_y = math.radians(2)/3600 # 2 [deg/hour]
# normal distribution param
sigma_a = 0.0005 * 9.8 # mg
sigma_g = math.radians(0.05) # 0.05 [deg/sec] 
Tg = 0.2
Ta = 0.3
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


#%% генерация массивов случайной составляющей
# 0,1,2 A_x,y,z
# 3,4,5 G_x,y,z
use_form_filter = False
D = data_gen(use_form_filter,
    [acc_offset_x, acc_offset_y],
    [gyr_drift_x, gyr_drift_y],
    [a_x, a_y, a_z],
    [w_x, w_y, w_z],
    sample_time, data_frequency,
    Ta, Tg,
    sigma_a, sigma_g,
    False
    )
#%%
na.nav().alignment_acc(mean(D[0]), mean(D[1]), mean(D[2]), heading)
pry = (
    [0]*(data_frequency*sample_time),
    [0]*(data_frequency*sample_time),
    [0]*(data_frequency*sample_time)
    )
vel = (
    [0]*(data_frequency*sample_time),
    [0]*(data_frequency*sample_time),
)
pos = (
    [0]*(data_frequency*sample_time),
    [0]*(data_frequency*sample_time),
)
for i in range(0, data_frequency*sample_time):
    if isinstance(D[0], list):
        na.nav().iter(
            (D[0])[i], (D[1])[i], (D[2])[i],
            (D[3])[i], (D[4])[i], (D[5])[i]
            )
    else:
        na.nav().iter(
            (D[0]), (D[1]), (D[2]),
            (D[3]), (D[4]), (D[5])
            )
    v = Tarr3f()
    na.nav().pry(v)
    for j in range(0,3):
        pry[j][i] = rad2min(v[j]-ini_pry[j])
    na.nav().vel(v)
    for j in range(0,2):
        vel[j][i] = v[j]
    v = Tarr2f()
    na.nav().pos(v)
    for j in range(0,2):
        pos[j][i] = rad2meters(v[j])

#%%
#conv = na.convert_data(na.DATA)
plots(pry,vel,pos, sample_time, data_frequency, title="моделир случ ", err=True, save=False)
#d = na.make_err_model() # считаем ошибку
#conv = na.convert_data(d) # переводим из си
#na.plot_model(conv, title="Моделирования случайной ошибки", save=True, err=True)

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
EQUAT = plot_err_formula(
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

#%%
print("Maximum difference between equational and alg pitch,roll")
for i in range(0,2):
    print(
        np.max(
        abs(
            EQUAT[0][i] - np.array(pry[i])
        )
        ) /60
    )

print("Maximum difference between equational vel and alg vel v_e, v_n")
for i in range(0,2):
    print(
        np.max(
        abs(
            EQUAT[1][i] - np.array(vel[i])
        )
        )
    )

print("Maximum difference between equational pos and alg pos lat, lon")
for i in range(0,2):
    print(
        np.max(
        abs(
            EQUAT[2][i] - np.array(pos[i])
        )
        ) /60
    )
print("misc")

#%% вычисление ошибок выставки
ae = NavIface(lat,lon, data_frequency)

na.nav().alignment_acc(mean(D[0]), mean(D[1]), mean(D[2]), heading)
res = na.nav().align_prh()
print(math.degrees(res[0]), math.degrees(res[1]), math.degrees(res[2]))
c_pitch = res[0]; c_roll = res[1]

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
