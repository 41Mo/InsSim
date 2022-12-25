#%%
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
sample_time = 5*60 # seconds
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
acc_offset_x = 1* 1e-3 * 9.8  # [m/s/s]
acc_offset_y = 1* 1e-3 * 9.8 # [m/s/s]
gyr_drift_x =  math.radians(10)/3600 # [rad/s]
gyr_drift_y =  math.radians(10)/3600
# normal distribution param
sigma_a = 0.019 #[m/s/s]
sigma_g = math.radians(0.3) # [rad/s]
gnss_std = m.radians((3/111111)/m.sqrt(1/data_frequency))
Tg = 0.2
Ta = 0.3
gnss_TIME = 43
gnss_OFF = 10*60
gnss_ON = gnss_OFF+ 5*60
rad_k = 10
ir_k = 10

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



def alg_loop(gnss_t:int, corr:bool=True, mid_off:bool=True, integ_rad_corr:bool =False, rad_corr:bool =False):

    na = NavIface(lat,lon,data_frequency)
    na.nav().alignment_acc(mean(D[0]), mean(D[1]), mean(D[2]), heading)
    #na.nav().alignment_rph(roll, pitch, heading)
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
    na.nav().gnss_T(gnss_t)
    na.nav().corr_mode(corr)
    na.nav().rad_set_k(rad_k)
    na.nav().integ_rad_set_k(ir_k)
    for i in range(0, data_frequency*sample_time):
        if isinstance(D[0], list):
            acc = [(D[0])[i], (D[1])[i], (D[2])[i]]
            gyr = [(D[3])[i], (D[4])[i], (D[5])[i]] 
            na.nav().iter_gnss(
                acc, gyr, gnss[i]
                )
        else:
            acc = [(D[0]), (D[1]), (D[2])]
            gyr = [(D[3]), (D[4]), (D[5])] 
            #g_p = [lat,lon]
            na.nav().iter_gnss(
                acc, gyr, gnss[i]
                )

        if (i == gnss_OFF*data_frequency and corr and mid_off):
            na.nav().corr_mode(False)
            na.nav().toggle_integ_rad_c(integ_rad_corr)
            na.nav().toggle_rad_c(rad_corr)
        if (i == gnss_ON*data_frequency and corr and mid_off):
            na.nav().corr_mode(True)
            na.nav().toggle_integ_rad_c(False)
            na.nav().toggle_rad_c(False)

        v = Tarr3d()
        na.nav().pry(v)
        for j in range(0,3):
            pry[j][i] = rad2min(v[j] - ini_pry[j])
        na.nav().vel(v)
        for j in range(0,2):
            test = v[j]
            vel[j][i] = v[j]
        v = Tarr2d()
        na.nav().pos(v)
        for j in range(0,2):
            pos[j][i] = rad2meters(v[j] - ini_pos[j])
    return (pry, vel, pos)



if True:
    gnss = rndnorm((lat, lon), gnss_std, size=(sample_time*data_frequency, 2)),
    gnss = np.squeeze(gnss)
else:
    gnss = []
    for i in range(0, data_frequency*sample_time):
        gnss.append([lat, lon])


# 0,1,2 A_x,y,z
# 3,4,5 G_x,y,z
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
#%%
ALG_DATA_CORR = alg_loop(gnss_t=gnss_TIME, corr=True, mid_off=True, integ_rad_corr=False,rad_corr=False)
#ALG_DATA_NOCORR = alg_loop(gnss_t=gnss_TIME, use_form_filter=False, corr=False)
ALG_DATA_CORR_2 = alg_loop(gnss_t=gnss_TIME, corr=True, mid_off=True, integ_rad_corr=True, rad_corr=False)
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
df = pd.DataFrame({
    "Time": np.linspace(0, sample_time/60, sample_time*data_frequency),
    "Theta_corr": ALG_DATA_CORR[0][0],
    "Gamma_corr": ALG_DATA_CORR[0][1],
    "Psi_corr": ALG_DATA_CORR[0][2],
    "Ve_corr": ALG_DATA_CORR[1][0],
    "Vn_corr": ALG_DATA_CORR[1][1],
    "phi_corr": ALG_DATA_CORR[2][0],
    "lamda_corr": ALG_DATA_CORR[2][1],
})
df2 = pd.DataFrame({
    "Time": np.linspace(0, sample_time/60, sample_time*data_frequency),
    "Theta_corr": ALG_DATA_CORR_2[0][0],
    "Gamma_corr": ALG_DATA_CORR_2[0][1],
    "Psi_corr":   ALG_DATA_CORR_2[0][2],
    "Ve_corr":    ALG_DATA_CORR_2[1][0],
    "Vn_corr":    ALG_DATA_CORR_2[1][1],
    "phi_corr":   ALG_DATA_CORR_2[2][0],
    "lamda_corr": ALG_DATA_CORR_2[2][1],
})
df1 = pd.DataFrame({ 
    "Time": np.linspace(0, sample_time/60, sample_time*data_frequency),
    "Theta_corr": EQUAT[0][0],
    "Gamma_corr": EQUAT[0][1],
    "Ve_corr":    EQUAT[1][0],
    "Vn_corr":    EQUAT[1][1],
    "phi_corr":   EQUAT[2][0],
    "lamda_corr": EQUAT[2][1],
})
#%%
# uncomment for interactive plots
#%matplotlib widget

plt.style.use('seaborn-white')
size = (204/25.4, 144.95/25.4)
dpi=300
axes = []
for i in range(2):
    ax_list = []
    for j in range(3):
        ax_list.append(
            plt.subplots(nrows=2, ncols=1, figsize=size)
        )
    axes.append(ax_list)
labels=[
    ['$\\theta$', '$\gamma$'],
    ['$V_e$', '$V_n$'],
    ['$\\varphi$', '$\lambda$'],
]
y_cols=[
    ["Theta_corr", "Gamma_corr"],
    ["Ve_corr","Vn_corr"],
    ["phi_corr", "lamda_corr"],
]
y_labels=[
    "Угловые минуты",
    "м/с",
    "м"
]
for d, ax in zip([df, df2],axes):
    show_legend = True 
    for tdf in [
        d.iloc[:gnss_OFF*data_frequency],
        d.iloc[gnss_OFF*data_frequency:gnss_ON*data_frequency],
        d.iloc[gnss_ON*data_frequency+60*data_frequency:]
    ]:
        plt_num = 0
        for y,y_label,a,label in zip(y_cols,y_labels,ax,labels):
            tdf.plot(
                x="Time", y=y,
                ax=a[1],
                grid=True,
                title=False,
                xlabel="Время, мин",
                ylabel=y_label,
                subplots=True,
                legend=show_legend,
                label=label,
            )
            plt_num+=1
        show_legend=False
#%%
# path = "images/"
# for ax_list, name in zip(axes, ["КОРР БИНС"," КОРР БИСО"]):
#     for ax,i in zip(ax_list,range(len(ax_list))):
#         ax[0].savefig(f"{path}{name} {i}.jpg", dpi=dpi)
#%%
start =sample_time*data_frequency-3*60*data_frequency
for dft in [df.iloc[start:],
            df2.iloc[start:]]:
    s = ''
    t = NavIface(lat,lon,data_frequency)
    t.nav().corr_mode(True)
    t.nav().gnss_T(gnss_TIME)
    Phiox = -acc_err_enu[1][0]/9.8 - t.nav().get_k(1)/(t.nav().get_k(0)+ t.nav().get_k(2))*gyr_drift_enu[0][0]
    Phioy = acc_err_enu[0][0]/9.8 - t.nav().get_k(1)/(t.nav().get_k(0)+ t.nav().get_k(2))*gyr_drift_enu[1][0]
    teta = (-(Phiox*m.cos(heading) - Phioy*m.sin(heading)))
    gama = (-(Phioy*m.cos(heading) + Phiox * m.sin(heading))*1/m.cos(pitch))
    s+=" "*6
    s+="Формульное Смоделированное\n"
    s+="Theta"
    s+=" "*3
    s+="%3.5f" % rad2min(teta)
    s+=" "*8
    s+="%3.5f" % np.mean(dft.loc[:,["Theta_corr"]].to_numpy())
    s+=" "*8
    s+="%3.5f\n" % np.std(dft.loc[:,["Theta_corr"]].to_numpy() - np.mean(dft.loc[:,["Theta_corr"]].to_numpy()))
    
    s+= "Gamma"
    s+=" "*2
    s+="%3.5f" % rad2min(gama)
    s+=" "*8
    s+="%3.5f" % np.mean(dft.loc[:,["Gamma_corr"]].to_numpy())
    s+=" "*8
    s+="%3.5f\n" % np.std(dft.loc[:,["Gamma_corr"]].to_numpy() - np.mean(dft.loc[:,["Gamma_corr"]].to_numpy()))
    
    s+="Vx"
    s+=" "*5
    s+="%3.5f" % (t.nav().get_k(0)/(t.nav().get_k(0)+t.nav().get_k(2))*gyr_drift_enu[1][0]*6378245.0)
    s+=" "*7
    s+="%3.5f" % np.mean(dft.loc[:,["Ve_corr"]].to_numpy())
    s+=" "*8
    s+="%3.5f\n" % np.std(dft.loc[:,["Ve_corr"]].to_numpy() - np.mean(dft.loc[:,["Ve_corr"]].to_numpy()))
    
    s+="Vy"
    s+=" "*6
    s+="%3.5f" % (-t.nav().get_k(0)/(t.nav().get_k(0)+t.nav().get_k(2))*gyr_drift_enu[0][0]*6378245.0)
    s+=" "*8
    s+="%3.5f" % np.mean(dft.loc[:,["Vn_corr"]].to_numpy())
    s+=" "*8
    s+="%3.5f\n" % np.std(dft.loc[:,["Vn_corr"]].to_numpy() - np.mean(dft.loc[:,["Vn_corr"]].to_numpy()))
    
    s+="Phi"
    s+=" "*5
    s+="%.5f" % rad2meters(-gyr_drift_enu[0][0]/(t.nav().get_k(0)+ t.nav().get_k(2)))
    s+=" "*8
    s+="%.5f" % np.mean(dft.loc[:,["phi_corr"]].to_numpy())
    s+=" "*8
    s+="%3.5f\n" % np.std(dft.loc[:,["phi_corr"]].to_numpy() - np.mean(dft.loc[:,["phi_corr"]].to_numpy()))
    
    s+="Lambda"
    s+=" "*1
    s+="%.5f" % rad2meters( gyr_drift_enu[1][0]/(t.nav().get_k(0)+ t.nav().get_k(2)) )
    s+=" "*7
    s+="%.5f" % np.mean(dft.loc[:,["lamda_corr"]].to_numpy())
    s+=" "*8
    s+="%3.5f\n" % np.std(dft.loc[:,["lamda_corr"]].to_numpy() - np.mean(dft.loc[:,["lamda_corr"]].to_numpy()))
    
    print(s)

#%%
s = ''
for i in range(3):
    s+= f"K{i+1}=%.3f\n" % t.nav().get_k(i)
print(s)
#%%
step = 1
start = 10
stop = 30
GNSS_T = [i for i in range(start,stop+step, step)]
s='                SKO\n'
s+='       | Theta   | Gamma   | \n'
for T in GNSS_T:
    inum =3
    mean_sko_Fx = 0
    mean_sko_Fy = 0
    #rad_k=T
    # ir_k = T
    for j in range(inum):
        angles = alg_loop(gnss_t=T, mid_off=False, corr=True, rad_corr=False, integ_rad_corr=False)[0]
        mean_sko_Fx += np.std(angles[0])#[gnss_ON*data_frequency+4*gnss_TIME*data_frequency:])
        mean_sko_Fy += np.std(angles[1])#[gnss_ON*data_frequency+4*gnss_TIME*data_frequency:])
    s+=f'T={T:4.0f} | {(mean_sko_Fx/inum):7.3f} | {(mean_sko_Fy/inum):7.3f} | {math.sqrt(math.pow(mean_sko_Fx/inum, 2)+math.pow(mean_sko_Fy/inum, 2)):7.3f}\n'
print(s)
#%%
"""
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

"""
#%% вычисление ошибок выставки
ae = NavIface(lat,lon, data_frequency)

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
