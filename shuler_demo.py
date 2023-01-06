#%%
import numpy as np
from InsSim.ins.ins import INS_SIM
from InsSim.imu.imu_model import IMU
from alg.shuler import Shuler
import matplotlib.pyplot as plt

R2D = 180/np.pi

# static test simulation
inital_param = np.array([
    np.array([0,0,0]), # att
    np.array([0,0,0]), # vel
    np.array([0,0,0]), # pos
])

sa = Shuler()

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
    inital_param,
    [sa],
    imu
)

sa.set_freq(ins.fs[0]) # setup alg loop frequency (shuler matches with imu)
runtime_sec = 90*60
ins.run(runtime_sec) # run (sec)

#%%
att, vel, pos = sa.error_eq(runtime_sec, np.array([imu._acc_bias, imu._gyro_bias]))
time_axis = np.linspace(0,runtime_sec,runtime_sec*sa.freq)

#%%
# compare simulated shuler ins output plots with error equations plots
fig, axs = plt.subplots(3,1)
labels = ['roll', 'pitch', 'heading']
for i in range(len(labels)):
    axs[i].plot(time_axis, ins.result("SH_ATT")[:,i]*R2D, label=labels[i])
    try:
        axs[i].plot(att[i], label="eq_"+labels[i])
        pass
    except:
        pass
    axs[i].set_xlabel("time, sec")
    axs[i].set_ylabel("deg")
    axs[i].legend()

fig, axs = plt.subplots(3,1)
labels = ['Ve', 'Vn', "Vu"]
for i in range(len(labels)):
    axs[i].plot(time_axis, ins.result("SH_VEL")[:,i], label=labels[i])
    try:
        axs[i].plot(vel[i], label="eq_"+labels[i])
        pass
    except:
        pass
    axs[i].set_xlabel("time, sec")
    axs[i].set_ylabel("m/s")
    axs[i].legend()

fig, axs = plt.subplots(3,1)
labels = ['lat', 'lng', "alt"]
y_labels = ['deg', 'deg', 'm']
for i in range(len(labels)):
    axs[i].plot(time_axis, ins.result("SH_POS")[:,i]*R2D, label=labels[i])
    try:
        axs[i].plot(pos[i], label="eq_"+labels[i])
        pass
    except:
        pass
    axs[i].set_xlabel("time, sec")
    axs[i].set_ylabel(y_labels[i])
    axs[i].legend()

plt.show()
#%%