
#%%
import math
import sys
sys.path.insert(0, '../modules/libnav/interface')
sys.path.insert(0, '../src/')
from interface import NavIface
import pandas as pd
import numpy as np
import matplotlib as mtpl
from matplotlib import pyplot as plt
from filter import filter
mtpl.style.use('fivethirtyeight')
#%%
def temp_lstsq(ini_temp, temp, Z):
    H = np.block([
        np.ones((points,1)),
        temp[:,np.newaxis]-ini_temp,
        np.power(temp[:,np.newaxis]-ini_temp,2)
        ]
        )
    X = np.linalg.lstsq(H,Z)[0]
    poly = X[0]+X[1]*temp+X[2]*np.power(temp,2)
    return X, poly

def temp_corr(ini_temp, temp, X, acc):
    return acc - (X[0]+X[1]*(temp-ini_temp)+X[2]*np.power(temp-ini_temp,2))

#%%
df = pd.read_csv('../csv_data/Temp.csv', delimiter=';')
acc = df.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
gyr = df.loc[:, ["Gyr_X", "Gyr_Y", "Gyr_Z"]].to_numpy()
temp = df["Temperature"].to_numpy()
points = len(temp)
frq= 100
time = points/frq/60
ini_temp = temp[0]
use_lowpass = True

#%%
if use_lowpass:
    acc_tmp = []
    for i in range(0,3):
        acc_tmp.append(filter(acc[:,i],10))
    acc_corr = []
    for i in range(0,len(acc_tmp[0])):
        tmp = []
        for j in range(0, 3):
            tmp.append(acc_tmp[j][i])
        acc_corr.append(tmp)
    acc = np.array(acc_corr)

#%%

a_k = []
a_poly = []
a_corr = []
for i in range(0,3):
    a_k_i, a_poly_i = temp_lstsq(ini_temp, temp, acc[:,i])
    a_k.append(a_k)
    a_poly.append(a_poly_i)
    a_corr_i = temp_corr(ini_temp,temp,a_k_i, acc[:,i])
    a_corr.append(
        a_corr_i
    )
#%%
df2 = pd.DataFrame({
    "Temperature": temp,
    "ax": acc[:,0],
    "ay": acc[:,1],
    "az": acc[:,2],
    "ax_poly":a_poly[0],
    "ay_poly":a_poly[1],
    "az_poly":a_poly[2],
    "ax_corr":a_corr[0],
    "ay_corr":a_corr[1],
    "az_corr":a_corr[2]
})

#%%
size = (140/25.4, 170/25.4)
fig = plt.figure()
ax = [
    fig.add_subplot(311),
    fig.add_subplot(312),
    fig.add_subplot(313),
]
plots = [
    ["ax", "ax_poly"],
    ["ay", "ay_poly"],
    ["ay", "ay_poly"]
]
for i in range(3):
    df2.plot(
        x="Temperature",
        y=plots[i],
        ax=ax[i],
        grid=True,
        sharex=True,
        figsize=size,
    )
# %%
size = (140/25.4, 170/25.4)
fig = plt.figure()
ax = [
    fig.add_subplot(311),
    fig.add_subplot(312),
    fig.add_subplot(313),
]
plots = [
    ["ax", "ax_corr"],
    ["ay", "ay_corr"],
    ["ay", "ay_corr"]
]
for i in range(3):
    df2.plot(
        x="Temperature",
        y=plots[i],
        ax=ax[i],
        grid=True,
        sharex=True,
        figsize=size,
    )
# %%
