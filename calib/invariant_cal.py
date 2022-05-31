
#%%
import sys
sys.path.insert(0, '../src/')
import pandas as pd
from filter import filter
from numpy import *
import matplotlib.pyplot as plt
def read_logs(path='logs'):
    path+='/'
    dataframes_list = []
    rows_to_skip=5
    dataframes_list.append(
        pd.read_csv(path+'00g.csv', delimiter=';', skiprows=rows_to_skip)
    )
    dataframes_list.append(
        pd.read_csv(path+'00-g.csv', delimiter=';', skiprows=rows_to_skip)
    )
    dataframes_list.append(
        pd.read_csv(path+'0g0.csv', delimiter=';', skiprows=rows_to_skip)
    )
    dataframes_list.append(
        pd.read_csv(path+'0-g0.csv', delimiter=';', skiprows=rows_to_skip)
    )
    dataframes_list.append(
        pd.read_csv(path+'g00.csv', delimiter=';', skiprows=rows_to_skip)
    )
    dataframes_list.append(
        pd.read_csv(path+'-g00.csv', delimiter=';', skiprows=rows_to_skip)
    )
    return dataframes_list

dfs = read_logs('../binary_output/invariant_cube/aks1')
acc = []
for df in dfs:
    acc.append(
        mean((df.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()),axis=0)
    )
#%%
g = 9.80665
ai = eye(3,3)
aii0 = zeros(shape=(3,3))
aii0[2,2] = 1
aij0 = zeros(shape=(3,3))
mu0 = zeros(shape=(3,3))
mu0[0,1] = -1; mu0[1,0] = 1
hi0 = zeros(shape=(3,2))
hi0[1,0] = 1; hi0[0,1] = -1

aii1 = aii0.copy()
aii1[2,2] = -1
aij1 = aij0.copy()
mu1 = mu0.copy()
mu1[0,1] = 1; mu1[1,0] = -1
hi1 = hi0.copy()

aii2 = zeros(shape=(3,3))
aii2[1,1] = 1;
aij2 = zeros(shape=(3,3))
aij2[2,2] = 1;
mu2 = zeros(shape=(3,3))
mu2[0, 2]=1; mu2[2,0]=-1
hi2 = zeros(shape=(3,2))
hi2[2,0] = -1; hi2[0,1] = -1

aii3 = aii2.copy()
aii3[1,1] = -1;
aij3 = aij2.copy()
aij3[2,2] = -1;
mu3 = mu2.copy()
mu3[0, 2]=-1; mu3[2,0]=1
hi3 = hi2.copy()

aii4 = zeros(shape=(3,3))
aii4[0,0] = 1
aij4 = zeros(shape=(3,3))
aij4[1,0] = 1; aij4[2, 1] = 1;
mu4 = zeros(shape=(3,3))
mu4[1,2] = -1; mu4[2,1] = 1;
hi4 = zeros(shape=(3,2))
hi4[1,0] = 1; hi4[2,1] = 1

aii5 = aii4.copy()
aii5[0,0] = -1
aij5 = aij4.copy()
aij5[1,0] = -1; aij5[2, 1] = -1;
mu5 = mu4.copy()
mu5[1,2] = 1; mu5[2,1] = -1;
hi5=hi4.copy()

#%%
H = array((
    block([
        ai, aii0, aij0,mu0,hi0
    ])*g,
    block([
        ai, aii1, aij1, mu1,hi1
    ])*g,
    block([
        ai, aii2, aij2, mu2,hi2
    ])*g,
    block([
        ai, aii3, aij3, mu3,hi3
    ])*g,
    block([
        ai, aii4, aij4, mu4,hi4
    ])*g,
    block([
        ai, aii5, aij5, mu5,hi5
    ])*g,


))
C = array((
    eye(3,3),
    array([
        [1,0,0],
        [0,1,0],
        [0,0,-1]
    ]),
    array([
        [1,0,0],
        [0,0,1],
        [0,-1,0]
    ]),
    array([
        [1,0,0],
        [0,0,-1],
        [0,-1,0]
    ]),
    array([
        [0,0,1],
        [0,1,0],
        [-1,0,0]
    ]),
    array([
        [0,0,-1],
        [0,1,0],
        [-1,0,0]
    ]),

))
G=matrix([[0],[0],[g]]) 

#%%
Z = []
for i in range(6):
    Z.append(acc[i][:,newaxis] - C[i]@G)

H_sum = H[0].transpose() @ H[0]
for i in range(1, 6):
    H_sum += H[i].transpose() @ H[i]
H_sum = linalg.inv(H_sum)

H_Z_sum = H[0].transpose() @ Z[0]
for i in range(1, 6):
    H_Z_sum += H[i].transpose() @ Z[i]

X =  H_sum @ H_Z_sum

estimation_pre = pd.DataFrame({
    "alpha_x" : X[0,0], "alpha_y": X[1,0], "alpha_z":X[2,0],
    "alpha_xx":X[3,0], "alpha_yy":X[4,0], "alpha_zz":X[5,0],
    "alpha_yz":X[6,0], "alpha_zx":X[7,0], "alpha_zy":X[8,0],
    "mu_x":X[9,0], "mu_y":X[10,0], "mu_z":X[11,0],
    "hi_x":X[12,0], "hi_y":array([X[13,0]] * 1, dtype="float"),
})
estimation_pre
#%%
H_Z_sum = zeros(shape=shape(H_Z_sum))
for i in range(3):
    ai_hat = matrix([
        [X[0,0]],
        [X[1,0]],
        [X[2,0]],
    ])
    aij_hat = matrix([
        [1+X[3,0],0,0],
        [X[6,0],1+X[4,0],0],
        [X[7,0],X[8,0],1+X[5,0]],
    ])
    mu_hat = matrix([
        [1,X[11,0],-X[10,0]],
        [-X[11,0],1,X[9,0]],
        [X[10,0],-X[9,0],1],
    ])
    hi_hat = matrix([
        [1, 0, -X[13,0]],
        [0,1,X[12,0]],
        [X[13,0],-X[12,0],1]
    ])
    Z_hat = ai_hat*g + aij_hat@mu_hat@C[i]@hi_hat@G - C[i]@G
    H_Z_sum += H[i].transpose() @ (Z[i]-Z_hat)
    X = X+H_sum @ H_Z_sum
estimation_fin = pd.DataFrame({
    "alpha_x" : X[0,0], "alpha_y": X[1,0], "alpha_z":X[2,0],
    "alpha_xx":X[3,0], "alpha_yy":X[4,0], "alpha_zz":X[5,0],
    "alpha_yz":X[6,0], "alpha_zx":X[7,0], "alpha_zy":X[8,0],
    "mu_x":X[9,0], "mu_y":X[10,0], "mu_z":X[11,0],
    "hi_x":X[12,0], "hi_y":array([X[13,0]] * 1, dtype="float"),
})
estimation_fin
#%% compensation test

dfn = pd.read_csv('../csv_data/Sensors_and_orientation.csv', delimiter=';')

t1= linalg.inv(matrix([
    [1+X[3,0], 0, 0],
    [1+X[6,0], 1+X[4,0],0],
    [X[7,0], X[8,0], 1+X[5,0]]
]))

dr = array([
    X[0,0],X[1,0],X[2,0]
])

a = dfn.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
#%%
points = len(a)
frq = 100
time = points/frq
time_axis = linspace(0, time, points)

for i in range(2):
    print("Было ax, ay, az")
    print((a[0])[:,newaxis])
    print("Стало ax, ay, az")
    print( t1@((a[0])[:,newaxis]-dr[:,newaxis]*g) )

result = []
for vec in a:
    result.append(
        t1@(vec[:,newaxis]-dr[:,newaxis]*g)
    )
result = array(result)
result = squeeze(result)
#%%
T=10
slice_from = 15000
res_df = pd.DataFrame({
    "Time":time_axis[slice_from:],
    "AccX_before_cal":(a[:,0])[slice_from:],
    "AccY_before_cal":(a[:,1])[slice_from:],
    "AccZ_before_cal":(a[:,2])[slice_from:],
    "AccX_after_cal": (result[:,0])[slice_from:],
    "AccY_after_cal": (result[:,1])[slice_from:],
    "AccZ_after_cal": (result[:,2])[slice_from:],
    "AccX_before_cal_f": filter(a[:,0], T=T)[slice_from:],
    "AccY_before_cal_f": filter(a[:,1], T=T)[slice_from:],
    "AccZ_before_cal_f": filter(a[:,2], T=T)[slice_from:],
    "AccX_after_cal_f": filter(result[:,0], T=T)[slice_from:],
    "AccY_after_cal_f": filter(result[:,1], T=T)[slice_from:],
    "AccZ_after_cal_f": filter(result[:,2], T=T)[slice_from:],
})
#%%
size = (140*2/25.4, 170*2/25.4)
plt.style.use('fivethirtyeight')
dump = res_df.plot(
    x="Time",
    subplots=True,
    layout=[3,2],
    figsize=size,
    y=[
        "AccX_before_cal", "AccX_after_cal",
        "AccY_before_cal", "AccY_after_cal",
        "AccZ_before_cal", "AccZ_after_cal",
    ]
)
#%%
size = (400/25.4, 170/25.4)
dump = res_df.plot(
    x="Time",
    figsize=size,
    y=[
        "AccX_before_cal_f", "AccX_after_cal_f",
        "AccY_before_cal_f", "AccY_after_cal_f",
    ]
)

dump = res_df.plot(
    x="Time",
    figsize=size,
    y=[
        "AccZ_before_cal_f", "AccZ_after_cal_f",
    ]
)

# %%
