
#%%
import sys
sys.path.insert(0, '../src/')
import pandas as pd
from matplotlib import pyplot as plt
from filter import filter
log_dir = 'logs/'
dfs = []
dfs.append(
    pd.read_csv(log_dir+'00g.csv', delimiter=';', skiprows=12)
)
dfs.append(
    pd.read_csv(log_dir+'00-g.csv', delimiter=';', skiprows=12)
)
dfs.append(
    pd.read_csv(log_dir+'0g0.csv', delimiter=';', skiprows=12)
)
dfs.append(
    pd.read_csv(log_dir+'0-g0.csv', delimiter=';', skiprows=12)
)
dfs.append(
    pd.read_csv(log_dir+'g00.csv', delimiter=';', skiprows=12)
)
dfs.append(
    pd.read_csv(log_dir+'-g00.csv', delimiter=';', skiprows=12)
)

acc = []
for df in dfs:
#acc = df.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
    acc.append(
        (df.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy())[int(df.shape[0]/2)]
    )
#%%
from numpy import *
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
    ]),
    block([
        ai, aii1, aij1, mu1,hi1
    ]),
    block([
        ai, aii2, aij2, mu2,hi2
    ]),
    block([
        ai, aii3, aij3, mu3,hi3
    ]),
    block([
        ai, aii4, aij4, mu4,hi4
    ]),
    block([
        ai, aii5, aij5, mu5,hi5
    ]),


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

# 0 0 g: Acc X: 0.00931, Acc Y: 0.21046, Acc Z: 10.057685
# 0 0 -g:Acc X: -0.00699, Acc Y: 0.14197, Acc Z: -9.5796832
# 0 g 0 : Acc X: -0.00373, Acc Y: 9.81994, Acc Z: 1.01122
# 0 -g 0: Acc X: -0.08805, Acc Y: -9.78619, Acc Z: -0.13522
# g 0 0: Acc X: 9.80955, Acc Y: 0.10599, Acc Z: 0.164297
# -g 0 0: Acc X: -9.82616, Acc Y: 0.08760, Acc Z: 0.545101

#a = array((
#    [[-0.002924], [0.011318], [10.026368]],
#    [[-0.00699], [0.14197], [-9.5796832]],
#    [[-0.00373], [9.81994], [1.01122]],
#    [[-0.08805], [-9.78619], [-0.13522]],
#    [[9.80955], [0.10599], [0.164297]],
#    [[-9.82616], [0.08760], [0.545101]],
#))
Z = []
for i in range(6):
    Z.append(acc[i][:,newaxis] - C[i]*G)

H_sum = H[0].transpose() @ H[0]
for i in range(1, 6):
    H_sum += H[i].transpose() @ H[i]
linalg.det(H_sum)

H_Z_sum = H[0].transpose() @ Z[0]
for i in range(1, 6):
    H_Z_sum += H[i].transpose() @ Z[i]
X = linalg.inv(H_sum) * H_Z_sum

estimation = pd.DataFrame({
    "alpha_x" : X[0,0],
    "alpha_y": X[1,0],
    "alpha_z":X[2,0],
    "alpha_xx":X[3,0],
    "alpha_yy":X[4,0],
    "alpha_zz":X[5,0],
    "alpha_yz":X[6,0],
    "alpha_zx":X[7,0],
    "alpha_zy":X[8,0],
    "mu_x":X[9,0],
    "mu_y":X[10,0],
    "mu_z":X[11,0],
    "hi_x":X[12,0],
    "hi_y":array([X[13,0]] * 1, dtype="float"),
})
#%%
#for i in range(6):
#    for j in range(3):
#        ai_hat = matrix([
#            [X[0,0]],
#            [X[1,0]],
#            [X[2,0]],
#        ])
#        aij_hat = matrix([
#            [X[3,0],0,0],
#            [X[6,0],X[4,0],0],
#            [X[7,0],X[8,0],X[5,0]],
#        ])
#        mu_hat = matrix([
#            [1,X[11,0],-X[10,0]],
#            [-X[11,0],1,X[9,0]],
#            [X[10,0],-X[9,0],1],
#        ])
#        hi_hat = matrix([
#            [1, 0, -X[13,0]],
#            [0,1,X[12,0]],
#            [X[13,0],-X[12,0],1]
#        ])
#        Z_hat = ai_hat*g + aij_hat*mu_hat*C[i]*G- C[i]*G
#        H_Z_sum += H[i].transpose() @ (Z[i]-Z_hat)
#        X = X+linalg.inv(H_sum) * H_Z_sum
#
#%%

#df = pd.read_csv('../csv_data/Sensors_and_orientation.csv', delimiter=';')

#t1= linalg.inv(matrix([
#    [1+X[3,0], 0, 0],
#    [1+X[6,0], 1+X[4,0],0],
#    [X[7,0], X[8,0], 1+X[5,0]]
#]))

t1= matrix([
    [1+X[3,0], 0, 0],
    [1+X[6,0], 1+X[4,0],0],
    [X[7,0], X[8,0], 1+X[5,0]]
])

dr = array([
    X[0,0],X[1,0],X[2,0]
])

for i in range(2):
    a = dfs[i].loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
    points = len(a)
    frq = 100
    time = points/frq
    time_axis = linspace(0, time, points)
    print("Было ax, ay, az")
    print((a[0])[:,newaxis])
    print("Стало ax, ay, az")
    print((a[0])[:,newaxis]-dr[:,newaxis]*g)
#print(t1@((a[0])[:,newaxis])-dr[:,newaxis])

# %%
(t1*(a - dr*g).transpose()).transpose()