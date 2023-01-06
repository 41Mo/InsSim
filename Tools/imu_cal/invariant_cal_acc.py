#!/bin/python3
import pandas as pd
from numpy import linalg, array, matrix, newaxis, squeeze, eye, zeros, mean, block, shape
import argparse
parser = argparse.ArgumentParser(description='Estiate acc errors.')
parser.add_argument('sd', metavar='srcdir', type=str,
                    help='Dir with acc data')
parser.add_argument('--out', dest="resfile", help="Store calib result in file. Can be .xlsx or .csv", default="")
parser.add_argument('--est_file', dest="ef", help="Use already estimated data file to check reult", default="")
parser.add_argument('--iter_n', dest="i_n", help="Num of approximation iter.", default=3, type=int)
args = parser.parse_args()
def read_logs(path='logs'):
    path+='/'
    dataframes_list = []
    dataframes_list.append(
        pd.read_csv(path+'00g.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'00-g.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'0g0.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'0-g0.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'g00.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'-g00.csv', delimiter=';', comment='/')
    )
    return dataframes_list

dfs = read_logs(args.sd)
acc = []
if args.ef:
    est_vec = pd.read_csv(args.ef).to_numpy().squeeze()

    t1= linalg.inv(matrix([
        [1+est_vec[3], 0, 0],
        [est_vec[6], 1+est_vec[4],0],
        [est_vec[7], est_vec[8], 1+est_vec[5]]
    ]))

    dr = array([
        est_vec[0],est_vec[1],est_vec[2]
    ])
for df in dfs:

    a = df.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
    if args.ef:
        result = []
        for vec in a:
            result.append(
                t1@(vec[:,newaxis]-dr[:,newaxis]*9.80665)
            )
        result = array(result)
        result = squeeze(result)
    else:
        result = a
    acc.append(
        mean(result,axis=0)
    )
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
#%%
H_Z_sum = zeros(shape=shape(H_Z_sum))
for i in range(args.i_n):
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
    'alpha_x' : X[0,0], "alpha_y": X[1,0], "alpha_z":X[2,0],
    "alpha_xx":X[3,0], "alpha_yy":X[4,0], "alpha_zz":X[5,0],
    "alpha_yz":X[6,0], "alpha_zx":X[7,0], "alpha_zy":X[8,0],
    "mu_x":X[9,0], "mu_y":X[10,0], "mu_z":X[11,0],
    "hi_x":X[12,0], "hi_y":array([X[13,0]] * 1, dtype="float"),
})
if args.resfile:
    estimation_fin.to_csv(args.resfile,index=False)
else:
    print(estimation_fin)
#estimation_fin.to_excel("../images/calib_t.xlsx",index=False)