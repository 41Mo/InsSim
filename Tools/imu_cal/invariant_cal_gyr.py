import pandas as pd
import numpy as np
from numpy import linalg, array, matrix, newaxis, squeeze, eye, zeros, mean, block, shape
import argparse
# parser = argparse.ArgumentParser(description='Estiate acc errors.')
# parser.add_argument('sd', metavar='srcdir', type=str,
#                     help='Dir with acc data')
# parser.add_argument('--out', dest="resfile", help="Store calib result in file. Can be .xlsx or .csv", default="")
# parser.add_argument('--est_file', dest="ef", help="Use already estimated data file to check reult", default="")
# parser.add_argument('--iter_n', dest="i_n", help="Num of approximation iter.", default=3, type=int)
# args = parser.parse_args()
def read_logs(path='logs'):
    path+='/'
    dataframes_list = []
    dataframes_list.append(
        pd.read_csv(path+'xccw.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'xcw.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'yccw.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'ycw.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'zccw.csv', delimiter=';', comment='/')
    )
    dataframes_list.append(
        pd.read_csv(path+'zcw.csv', delimiter=';', comment='/')
    )
    return dataframes_list

# dfs = read_logs(args.sd)
dfs = read_logs("old/binary_output/invariant_cube_2/gyr2")

ux = -0.01729
uy = 0.009018
uz = -0.01878

C=matrix([
    [1,uz,-uy],
    [-uz,1,ux],
    [uy,-ux,1]
])

theta = array([8,-8,6,-6,6,-6])*2*np.pi
Ti = []
dt = 0.01
omega = []
# if args.ef:
#     est_vec = pd.read_csv(args.ef).to_numpy().squeeze()

#     t1= linalg.inv(matrix([
#         [1+est_vec[3], 0, 0],
#         [est_vec[6], 1+est_vec[4],0],
#         [est_vec[7], est_vec[8], 1+est_vec[5]]
#     ]))

#     dr = array([
#         est_vec[0],est_vec[1],est_vec[2]
#     ])
for df in dfs:
    g = df[["Gyr_X", "Gyr_Y", "Gyr_Z"]].to_numpy().T
    # if args.ef:
    #     result = []
    #     for vec in a:
    #         result.append(
    #             t1@(vec[:,newaxis]-dr[:,newaxis]*9.80665)
    #         )
    #     result = array(result)
    #     result = squeeze(result)
    # else:
    #     result = a
    Ti.append(np.shape(g)[1]*dt)
    omega.append(
        np.sum(g,axis=1)*dt
    )

H = array([
    [
        [Ti[0],0,0,theta[0],0,0,-theta[0]*uz,theta[0]*uy,0,0,0,0],
        [0,Ti[0],0,0,-theta[0]*uz,0,0,0,theta[0],theta[0]*uy,0,0],
        [0,0,Ti[0],0,0,theta[0]*uy,0,0,0,0,theta[0],-theta[0]*uz]
    ],
    [
        [Ti[1],0,0,theta[1],0,0,-theta[1]*uz,theta[1]*uy,0,0,0,0],
        [0,Ti[1],0,0,-theta[1]*uz,0,0,0,theta[1],theta[1]*uy,0,0],
        [0,0,Ti[1],0,0,theta[1]*uy,0,0,0,0,theta[1],-theta[1]*uz]
    ],
    [
        [Ti[2],0,0,theta[2]*uz,0,0,theta[2],-theta[2]*ux,0,0,0,0],
        [0,Ti[2],0,0,theta[2],0,0,0,theta[2]*uz,-theta[2]*ux,0,0],
        [0,0,Ti[2],0,0,-theta[2]*ux,0,0,0,0,theta[2]*uz,theta[2]]
    ],
    [
        [Ti[3],0,0,theta[3]*uz,0,0,theta[3],-theta[3]*ux,0,0,0,0],
        [0,Ti[3],0,0,theta[3],0,0,0,theta[3]*uz,-theta[3]*ux,0,0],
        [0,0,Ti[3],0,0,-theta[3]*ux,0,0,0,0,theta[3]*uz,theta[3]]
    ],
    [
        [Ti[4],0,0,-theta[4]*uy,0,0,theta[4]*ux,theta[4],0,0,0,0],
        [0,Ti[4],0,0,theta[4]*ux,0,0,0,-theta[4]*uy,theta[4],0,0],
        [0,0,Ti[4],0,0,theta[4],0,0,0,0,-theta[4]*uy,theta[4]*ux]
    ],
    [
        [Ti[5],0,0,-theta[5]*uy,0,0,theta[5]*ux,theta[5],0,0,0,0],
        [0,Ti[5],0,0,theta[5]*ux,0,0,0,-theta[5]*uy,theta[5],0,0],
        [0,0,Ti[5],0,0,theta[5],0,0,0,0,-theta[5]*uy,theta[5]*ux]
    ]
])

Z = []
Theta = array([
    [theta[0],0,0],
    [theta[1],0,0],
    [0,theta[2],0],
    [0,theta[3],0],
    [0,0,theta[4]],
    [0,0,theta[5]]
])
for i in range(6):
    Z.append((omega[i][:,newaxis] - C@(Theta[i][:,newaxis])))

H_sum = H[0].transpose() @ H[0]
for i in range(1, 6):
    H_sum += H[i].transpose() @ H[i]
H_sum = linalg.inv(H_sum)

H_Z_sum = H[0].transpose() @ Z[0]
for i in range(1, 6):
    H_Z_sum += H[i].transpose() @ Z[i]

X =  H_sum @ H_Z_sum

estimation_pre = {
    "beta_x" : X[0,0], "beta_y": X[1,0], "beta_z":X[2,0],
    "beta_xx":X[3,0], "beta_yy":X[4,0], "beta_zz":X[5,0],
    "beta_xy":X[6,0], "beta_xz":X[7,0], "beta_yx":X[8,0],
    "beta_yz":X[9,0], "beta_zx":X[10,0], "beta_zy":X[11,0]
}
print(estimation_pre)
exit(0)
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