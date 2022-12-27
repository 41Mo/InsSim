#%%
import numpy as np
from InsSim.ins.ins import INS_SIM
from InsSim.imu.imu_model import IMU
from alg.free_integration import FIA
import matplotlib.pyplot as plt

R2D = 180/np.pi


# static test simulation
inital_param = np.array([
    np.array([0,0,0]), # att
    np.array([0,0,0]), # vel
    np.array([0,0,0]), # pos
])

fia = FIA(
    inital_param[0], # setup initial att
    inital_param[1], # setup initial vel
    inital_param[2], # setup initial pos
    use_prec_geoparm=True
)

imu = IMU({
    'accel_b'  : np.array([0,0,0]),
    'accel_std': np.array([0,0,0]),
    'accel_tau': np.array([1,1,1]),
    'gyro_b'   : np.array([1,1,0]),
    'gyro_std' : np.array([0,0,0]),
    'gyro_tau' : np.array([1,1,1]),
})

ins = INS_SIM(
    np.array([1,0,0]), # frequency [imu, gnss, mag]
    inital_param[0],
    fia,
    imu
)
fia.set_freq(ins.fs[0]) # setup alg loop frequency ( shuler matches with imu)

ins.run(180*60) # run (sec)


# compare simulated shuler ins output plots with error equations plots
#%%
att, vel, pos = ins.error_eq(180*60)
fig, axs = plt.subplots(3,1)
labels = ['roll', 'pitch', 'heading']
for i in range(2):
    axs[i].plot(ins.result("ATT")[:,i]*R2D*60, label=labels[i])
    axs[i].plot(att[i], label=labels[i]+'_r')
    axs[i].legend()
# %%
fig, axs = plt.subplots(2,1)
labels = ['Ve', 'Vn']
for i in range(2):
    axs[i].plot(ins.result("SPD")[:,i], label=labels[i])
    axs[i].plot(vel[i], label=labels[i]+'_r')
    axs[i].legend()

#%%
fig, axs = plt.subplots(2,1)
labels = ['lat', 'lng']
for i in range(2):
    axs[i].plot(ins.result("POS")[:,i]*R2D, label=labels[i])
    axs[i].legend()

plt.show()