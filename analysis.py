#%%
from src.nav_alg import nav_alg, plots
import numpy as np
#%%
# Moscow
lat = 0#55.75
lon = 0#37.61

# file with real sensors data
data_file = "csv_data/Sensors_and_orientation.csv"

# sensor errors
g=9.81
gyr_offset = np.deg2rad(0.1) # [deg/sec]
acc_offset = 0.002/g # 2 [mg]
acc_drift = 0.00001/g # 0.1 [mg]
gyr_drift = np.deg2rad(10)/3600 # [deg/hour]

# %%
gyro_offset_analysis = nav_alg()
gyro_offset_analysis.set_w_body(gyr_offset, gyr_offset, gyr_offset)
gyro_offset_analysis.set_coordinates(lat, lon)

acc_offset_analysis = nav_alg()
acc_offset_analysis.set_a_body(acc_offset, acc_offset, acc_offset)
acc_offset_analysis.set_coordinates(lat, lon)

acc_drift_analysis = nav_alg()
acc_drift_analysis.set_a_body(acc_drift, acc_drift, acc_drift)
acc_drift_analysis.set_coordinates(lat, lon)

gyro_drift_analysis= nav_alg()
gyro_drift_analysis.set_w_body(gyr_drift, gyr_drift, gyr_drift)
gyro_drift_analysis.set_coordinates(lat, lon)

#%%
from src.csv_parser import get_data_from_csv
SENSOR_DATA_GYR = get_data_from_csv("Gyr_X","Gyr_Y","Gyr_Z", file_name=data_file)
gyro_random_error_analysis = nav_alg(frequency=100, analysis="dynamic_gyro", points_count=len(SENSOR_DATA_GYR["Gyr_X"]))
gyro_random_error_analysis.set_coordinates(lat, lon)

SENSOR_DATA_GYR.update({ "Gyr_X":np.deg2rad(SENSOR_DATA_GYR["Gyr_X"]-np.mean(SENSOR_DATA_GYR["Gyr_X"])) })
SENSOR_DATA_GYR.update({ "Gyr_Y":np.deg2rad(SENSOR_DATA_GYR["Gyr_Y"]-np.mean(SENSOR_DATA_GYR["Gyr_Y"])) })
SENSOR_DATA_GYR.update({ "Gyr_Z":np.deg2rad(SENSOR_DATA_GYR["Gyr_Z"]-np.mean(SENSOR_DATA_GYR["Gyr_Z"])) })

gyro_random_error_analysis.sensor_data = SENSOR_DATA_GYR

# %%
SENSOR_DATA_ACC = get_data_from_csv("Acc_X","Acc_Y","Acc_Z", file_name=data_file)
acc_random_error_analysis = nav_alg(frequency=1000, analysis="dynamic_acc", points_count=len(SENSOR_DATA_ACC["Acc_X"]))
acc_random_error_analysis.set_coordinates(lat, lon)

SENSOR_DATA_ACC.update({ "Acc_X":(SENSOR_DATA_ACC["Acc_X"]-np.mean(SENSOR_DATA_ACC["Acc_X"])) })
SENSOR_DATA_ACC.update({ "Acc_Y":(SENSOR_DATA_ACC["Acc_Y"]-np.mean(SENSOR_DATA_ACC["Acc_Y"])) })
SENSOR_DATA_ACC.update({ "Acc_Z":(SENSOR_DATA_ACC["Acc_Z"]-np.mean(SENSOR_DATA_ACC["Acc_Z"])) })

acc_random_error_analysis.sensor_data = SENSOR_DATA_ACC

#%%
SENSOR_DATA = get_data_from_csv("Acc_X","Acc_Y","Acc_Z", "Gyr_X", "Gyr_Y", "Gyr_Z", file_name=data_file)
random_error_analysis = nav_alg(frequency=1000, analysis="dynamic_both", points_count=len(SENSOR_DATA["Acc_X"]))
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

crete_threads_and_run_1(
    acc_offset_analysis,
    gyro_offset_analysis,
    acc_drift_analysis,
    gyro_drift_analysis,
    gyro_random_error_analysis,
    acc_random_error_analysis,
    random_error_analysis
    )

# %%
plots(acc_offset_analysis)

# %%
plots(gyro_offset_analysis)

# %%
plots(acc_drift_analysis)

# %%
plots(gyro_drift_analysis)

# %%
plots(gyro_random_error_analysis)

# %%
plots(acc_random_error_analysis)

#%%
plots(random_error_analysis)

#%%