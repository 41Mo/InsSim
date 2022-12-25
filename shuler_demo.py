#%%
import numpy as np
from InsSim.ins.ins import INS_SIM
from InsSim.imu.imu_model import IMU
from alg.free_integration import FIA

fia = FIA()

imu = IMU({
    'accel_b'  : np.array([1,1,0]),
    'accel_std': np.array([0,0,0]),
    'accel_tau': np.array([0,0,0]),
    'gyro_b'   : np.array([1,1,0]),
    'gyro_std' : np.array([0,0,0]),
    'gyro_tau' : np.array([0,0,0]),
})

ins = INS_SIM(
    np.array([1,1,1]), #fs
    np.array([0,0,0]), # pos
    np.array([0,0,0]), # att
    fia,
    imu
)

ins.run(180*60) # run for 100 sec
att, vel, pos = ins.error_eq(180*60)

R2D = 180/np.pi
import matplotlib.pyplot as plt
# %matplotlib widget

# %%

fig, axs = plt.subplots(3,1)
labels = ['roll', 'pitch', 'heading']
for i in range(2):
    axs[i].plot(ins.result("ATT")[i]*R2D*60, label=labels[i])
    axs[i].plot(att[i], label=labels[i]+'_r')
    axs[i].legend()
# %%
fig, axs = plt.subplots(2,1)
labels = ['Ve', 'Vn']
for i in range(2):
    axs[i].plot(ins.result("SPD")[i], label=labels[i])
    axs[i].plot(vel[i], label=labels[i]+'_r')
    axs[i].legend()

#%%
fig, axs = plt.subplots(2,1)
labels = ['lat', 'lng']
for i in range(2):
    axs[i].plot(ins.result("POS")[i]*R2D, label=labels[i])
    axs[i].legend()

#%%
