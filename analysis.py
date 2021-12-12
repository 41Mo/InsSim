#%%
from src.nav_alg import nav_alg,matrix_enu_to_body
import numpy as np
#%%
# Moscow
lat = 55.75
lon = 37.61

# file with real sensors data
data_file = "csv_data/Sensors_and_orientation.csv"

# sensor errors
g=9.81
gyr_offset = np.deg2rad(0.1) # [deg/sec]
acc_offset = 0.002/g # 2 [mg]
acc_drift = 0.00001/g # 0.1 [mg]
gyr_drift = np.deg2rad(10)/3600 # [deg/hour]

#%%
# alignemnt errors [deg]
# 0 - assuming no errors
psi = 0
teta = 0
gamma = 0
# assuming we are standing steel
a_enu = np.array([[0],[0],[g]])

C_enu_body = matrix_enu_to_body(psi, teta, gamma)
# re-project vect
a_body = C_enu_body @ a_enu

# %%
gyro_offset_analysis = nav_alg()
gyro_offset_analysis.set_w_body(gyr_offset, gyr_offset, gyr_offset)
gyro_offset_analysis.set_coordinates(lat, lon)

acc_offset_analysis = nav_alg(frequency=1, time=10800)
acc_offset_analysis.set_a_body(a_body[0][0], a_body[1][0], a_body[2][0])
acc_offset_analysis.set_coordinates(lat, lon)

acc_drift_analysis = nav_alg()
acc_drift_analysis.set_a_body(a_body[0][0], a_body[1][0], a_body[2][0])
acc_drift_analysis.set_coordinates(lat, lon)

gyro_drift_analysis= nav_alg()
gyro_drift_analysis.set_w_body(gyr_drift, gyr_drift, gyr_drift)
gyro_drift_analysis.set_coordinates(lat, lon)

#%%
from src.csv_parser import get_data_from_csv
SENSOR_DATA_GYR = get_data_from_csv("Gyr_X","Gyr_Y","Gyr_Z", file_name=data_file)
gyro_random_error_analysis = nav_alg(analysis="dynamic_gyro", time=1800, frequency=100)
gyro_random_error_analysis.set_coordinates(lat, lon)

SENSOR_DATA_GYR.update({ "Gyr_X":np.deg2rad(SENSOR_DATA_GYR["Gyr_X"]-np.mean(SENSOR_DATA_GYR["Gyr_X"])) })
SENSOR_DATA_GYR.update({ "Gyr_Y":np.deg2rad(SENSOR_DATA_GYR["Gyr_Y"]-np.mean(SENSOR_DATA_GYR["Gyr_Y"])) })
SENSOR_DATA_GYR.update({ "Gyr_Z":np.deg2rad(SENSOR_DATA_GYR["Gyr_Z"]-np.mean(SENSOR_DATA_GYR["Gyr_Z"])) })

gyro_random_error_analysis.sensor_data = SENSOR_DATA_GYR

# %%
SENSOR_DATA_ACC = get_data_from_csv("Acc_X","Acc_Y","Acc_Z", file_name=data_file)
acc_random_error_analysis = nav_alg(analysis="dynamic_acc", time=1800, frequency=100)
acc_random_error_analysis.set_coordinates(lat, lon)

SENSOR_DATA_ACC.update({ "Acc_X":(SENSOR_DATA_ACC["Acc_X"]-np.mean(SENSOR_DATA_ACC["Acc_X"])) })
SENSOR_DATA_ACC.update({ "Acc_Y":(SENSOR_DATA_ACC["Acc_Y"]-np.mean(SENSOR_DATA_ACC["Acc_Y"])) })
SENSOR_DATA_ACC.update({ "Acc_Z":(SENSOR_DATA_ACC["Acc_Z"]-np.mean(SENSOR_DATA_ACC["Acc_Z"])) })

acc_random_error_analysis.sensor_data = SENSOR_DATA_ACC

#%%
SENSOR_DATA = get_data_from_csv("Acc_X","Acc_Y","Acc_Z", "Gyr_X", "Gyr_Y", "Gyr_Z", file_name=data_file)
random_error_analysis = nav_alg(analysis="dynamic_both", time=1800, frequency=100)
random_error_analysis.set_coordinates(lat, lon)

SENSOR_DATA.update({ "Acc_X":(SENSOR_DATA["Acc_X"]-np.mean(SENSOR_DATA["Acc_X"])) })
SENSOR_DATA.update({ "Acc_Y":(SENSOR_DATA["Acc_Y"]-np.mean(SENSOR_DATA["Acc_Y"])) })
SENSOR_DATA.update({ "Acc_Z":(SENSOR_DATA["Acc_Z"]-np.mean(SENSOR_DATA["Acc_Z"])) })

SENSOR_DATA.update({ "Gyr_X":np.deg2rad(SENSOR_DATA["Gyr_X"]-np.mean(SENSOR_DATA["Gyr_X"])) })
SENSOR_DATA.update({ "Gyr_Y":np.deg2rad(SENSOR_DATA["Gyr_Y"]-np.mean(SENSOR_DATA["Gyr_Y"])) })
SENSOR_DATA.update({ "Gyr_Z":np.deg2rad(SENSOR_DATA["Gyr_Z"]-np.mean(SENSOR_DATA["Gyr_Z"])) })

random_error_analysis.sensor_data = SENSOR_DATA
# %%
import threading
    
def crete_threads_and_run_1(*objects):
    threads = []
    for object in objects:
       threads.append(threading.Thread(target=object.analysis))
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()

#crete_threads_and_run_1(
#    acc_offset_analysis,
#    gyro_offset_analysis,
#    acc_drift_analysis,
#    gyro_drift_analysis,
#    gyro_random_error_analysis,
#    acc_random_error_analysis,
#    random_error_analysis
#    )

# %%
acc_offset_analysis.analysis()
acc_offset_analysis.plots()

# %%
gyro_offset_analysis.plots()

# %%
acc_drift_analysis.plots()

# %%
gyro_drift_analysis.plots()

# %%
gyro_random_error_analysis.plots()

# %%
acc_random_error_analysis.plots()

#%%
random_error_analysis.plots()

#%%