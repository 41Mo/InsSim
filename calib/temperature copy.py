
#%%
import math
import sys
sys.path.insert(0, '../modules/libnav/interface')
sys.path.insert(0, '../src/')
import pandas as pd
import numpy as np
from numpy import linalg as linalg
from numpy import matrix, array, newaxis, squeeze
import matplotlib as mtpl
from matplotlib import pyplot as plt
from filter import filter
mtpl.style.use('seaborn-white')
#%%
def temp_lstsq(ini_temp, temp, Z):
    points = len(temp)
    H = np.block([
        np.ones((points,1)),
        temp[:,np.newaxis]-ini_temp,
        np.power(temp[:,np.newaxis]-ini_temp,2)
        ]
        )
    X = np.linalg.lstsq(H,Z, rcond=None)[0]
    return X
def make_poly(temp, X):
    return X[0]+X[1]*temp+X[2]*np.power(temp,2)
def temp_corr(ini_temp, temp, X, acc):
    return acc - (X[0]+X[1]*(temp-ini_temp)+X[2]*np.power(temp-ini_temp,2))
def inters(df1, df2):
    result1 = []
    result2 = []
#buf.loc[buf.Temperature>22]
    for idx1, row1 in df1.iterrows():
        for idx2, row2 in df2.loc[df2.Temperature == row1.Temperature].iterrows():
            if row1.Temperature == row2.Temperature and not(idx1 in result1) and not(idx2 in result2):
                result1.append(idx1)
                result2.append(idx2)
                break
            if row2.Temperature > row1.Temperature:
                break
    return result1, result2
def flt(acc):
    acc_tmp = []
    for i in range(0,3):
        acc_tmp.append(filter(acc[:,i],10))
    acc_tmp = np.array(acc_tmp)
    acc=np.block([
        (acc_tmp[0])[:,np.newaxis],
        (acc_tmp[1])[:,np.newaxis],
        (acc_tmp[2])[:,np.newaxis],
    ])
    return acc

def print_poly(Z, poly_coeff, temp):
    poly = make_poly(temp, poly_coeff)
    plt.figure(figsize = (243/25.4, 147/25.4))
    plt.plot(
        temp,
        Z,
        label="$\\frac{Z_2^g+Z_2^{-g}}{2g}$",
        )
    plt.plot(
        temp,
        poly,
        label="Полином"
        )
    plt.title("Описание температурной зависимости смещения нуля МНК")
    plt.xlabel("Температура, град")
    #plt.ylabel("g")
    plt.legend()
    plt.savefig("../images/t_cal.jpg", dpi=800)
    plt.show()
G = 9.80665
#%%
#df = pd.read_csv(, delimiter=';', comment="/")
est_vec = pd.read_csv("../tmp/r1.csv").to_numpy().squeeze()

t1= linalg.inv(matrix([
    [1+est_vec[3], 0, 0],
    [est_vec[6], 1+est_vec[4],0],
    [est_vec[7], est_vec[8], 1+est_vec[5]]
]))

dr = array([
    est_vec[0],est_vec[1],est_vec[2]
])
dfs = []
res = []
files = [
    '../binary_output/temperature/g00.csv',
    '../binary_output/temperature/-g00.csv',
    '../binary_output/temperature/0g0.csv',
    '../binary_output/temperature/0-g0.csv',
    '../binary_output/temperature/00g.csv',
    '../binary_output/temperature/00-g.csv',
    ]
for f in files:
    buf = pd.read_csv(f, delimiter=';', comment="/")
    #del buf['PacketCounter']
    # buf = buf.loc[buf.Temperature>]
    buf = buf.loc[buf.Temperature<20]

    a_v = buf.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()

    result = []
    for vec in a_v:
        result.append(
            t1@(vec[:,newaxis]-dr[:,newaxis]*9.80665)
        )
    result = array(result)
    result = squeeze(result)

    buf.Acc_X = result[:,0]
    buf.Acc_Y = result[:,1]
    buf.Acc_Z = result[:,2]

    dfs.append(
        buf
        )
Sets= [
    "Acc_X",
    "Acc_X",
    "Acc_Y",
    "Acc_Y",
    "Acc_Z",
    "Acc_Z",
]

#%%
#%%

i = 0
while i < len(dfs):
    min_size = np.min([
        np.shape(dfs[i])[0],
        np.shape(dfs[i+1])[0]
    ])
    # old variant
    dfs[i] = dfs[i].iloc[:min_size]
    dfs[i+1] = dfs[i+1].iloc[:min_size]

    # new variant
    #i1, i2 = inters(dfs[i], dfs[i+1])
    #dfs[i] = pd.DataFrame(dfs[i], index=i1)
    #dfs[i+1] = pd.DataFrame(dfs[i+1], index=i2)

    i+=2
#%%
for df, s in zip(dfs, Sets):
    df.plot(
        y=s,
        x="Temperature"
    )
#%%
Z_sum= []
Z_sub = []
temperatures=[]
i = 0
while i < len(dfs):
    Z_sum.append(
        ((dfs[i]
        .loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]]
        .to_numpy() +
        dfs[i+1]
        .loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]]
        .to_numpy())/(2*G)
        )
    )
    Z_sub.append(
        (((dfs[i]
        .loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]]
        .to_numpy() -
        dfs[i+1]
        .loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]]
        .to_numpy())/(2*G))-1
        )
    )
    temperatures.append(
        (dfs[i].Temperature.to_numpy(),
        dfs[i+1].Temperature.to_numpy())
    )
    i+=2
#%%
a_x = []
a_xx = []
for Z1, Z2, i, t in zip(Z_sum, Z_sub, range(len(Z_sum)), temperatures):
    t1 = t[0]
    t2 = t[1]
    a_x.append(temp_lstsq(t1[0], t1, Z1[:,i]))
    a_xx.append(temp_lstsq(t2[0], t2, Z2[:,i]))
#%%
print_poly(Z_sum[2][:,2], a_x[2],temperatures[2][0]-temperatures[2][0][0])
#%%
print_poly(Z_sub[2][:,2], a_xx[2], temperatures[2][1]-temperatures[2][1][0])

#%%
for Z1, Z2, i, t in zip(Z_sum, Z_sub, range(len(Z_sum)), temperatures):
    t1 = t[0]-t[0][0]
    t2 = t[1]-t[1][0]
    print_poly(Z1[:,i], a_x[i],t1)
    print_poly(filter(Z1[:,i]), a_x[i], t1) 

    print_poly(Z2[:,i], a_xx[i], t2)
    print_poly(filter(Z2[:,i]), a_xx[i], t2)
#%%
sets = [0, 0, 1, 1, 2, 2]
for df, s in zip(dfs, sets):
    acc = df.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
    corrected = []
    temperature = df.Temperature.to_numpy()
    for i in range(np.shape(acc)[0]):
        M1 = np.linalg.inv(
            np.matrix([
            [1+make_poly(temperature[i],a_xx[0]), 0, 0],
            [0, 1+make_poly(temperature[i],a_xx[1]), 0],
            [0, 0, 1+make_poly(temperature[i],a_xx[1])]
            ])
        )
        M2= np.array([
            [make_poly(temperature[i],a_x[0])],
            [make_poly(temperature[i],a_x[1])],
            [make_poly(temperature[i],a_x[2])]
        ])*G
        corrected.append(
            (acc[i][:,np.newaxis]- M2)
        )
    corrected = np.squeeze(corrected)
    plt.plot(
        temperature,
        filter(acc[:,s],100),
        label="do",
    )
    plt.plot(
        temperature,
        filter(corrected[:,s],100),
        label="posle",
    )
    plt.legend()
    plt.show()
# %%
df = dfs[4]
#df = pd.read_csv(files[4], delimiter=';', comment="/")
acc = df.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
corrected = []
temperature = df.Temperature.to_numpy()
temp = temperature-6
for i in range(np.shape(acc)[0]):
    t = temp[i]
    M1 = np.linalg.inv(
        np.matrix([
        [1+make_poly(t,a_xx[0]), 0, 0],#[1,0,0],#
        [0, 1+make_poly(temperature[i],a_xx[1]), 0],#[0,1,0],#
        [0, 0, 1+make_poly(t,a_xx[2])],#[0,0,1]#
        ])
    )
    M2= np.array([
        [make_poly(t,a_x[0])],#[0],#
        [make_poly(temperature[i],a_x[1])],#[0],#
        [make_poly(t,a_x[2])],#[0],#
    ])*G
    corrected.append(
        M1@(acc[i][:,np.newaxis]- M2)
    )
corrected = np.squeeze(corrected)
sets = [
    ("Канал X", 0),
    ("Канал Y", 1),
    ("Канал Z", 2),
]

for title, s in sets:
    plt.figure(figsize = (300/25.4, 147/25.4))
    plt.plot(
        temperature,
        filter(acc[:,s],10),
        #acc[:,s],
        label="до калибровки",
    )
    plt.plot(
        temperature,
        filter(corrected[:,s],10),
        #corrected[:,s],
        label="после калибровки",
    )
    plt.xlabel("Температура, град")
    plt.ylabel("$\\frac{м}{с^2}$")
    plt.title(title)
    plt.legend()
    plt.savefig(f"../images/t_calib_{title}.jpg", dpi=800, bbox_inches="tight")
    plt.show()

# %%
