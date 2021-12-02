#%%
from nav_alg import nav_alg, plots
import numpy as np
# %%
gyro_offset_analysis = nav_alg()
gyr_offset = np.deg2rad(0.1)
gyro_offset_analysis.set_w_body(gyr_offset, gyr_offset, gyr_offset)
gyro_offset_analysis.set_coordinates(55.75, 37.61)

acc_offset_analysis = nav_alg()
acc_offset = 0.002/9.81
acc_offset_analysis.set_a_body(acc_offset, acc_offset, acc_offset)
acc_offset_analysis.set_coordinates(55.75, 37.61)

acc_drift_analysis = nav_alg()
acc_drift = 0.00001 / 9.81
acc_drift_analysis.set_a_body(acc_drift, acc_drift, acc_drift)
acc_drift_analysis.set_coordinates(55.75, 37.61)

gyro_drift_analysis= nav_alg()
gyr_drift = np.deg2rad(10)/3600
gyro_drift_analysis.set_w_body(gyr_drift, gyr_drift, gyr_drift)
gyro_drift_analysis.set_coordinates(55.75, 37.61)

#%%
from csv_parser import get_data_from_csv
SENSOR_DATA_GYR = get_data_from_csv("Gyr_X","Gyr_Y","Gyr_Z", file_name="csv_data/Sensors_and_orientation.csv")
gyro_random_error_analysis = nav_alg(frequency=100, analysis="dynamic_gyro", points_count=len(SENSOR_DATA_GYR["Gyr_X"]))
gyro_random_error_analysis.set_coordinates(55.75, 37.61)

SENSOR_DATA_GYR.update({ "Gyr_X":np.deg2rad(SENSOR_DATA_GYR["Gyr_X"]-np.mean(SENSOR_DATA_GYR["Gyr_X"])) })
SENSOR_DATA_GYR.update({ "Gyr_Y":np.deg2rad(SENSOR_DATA_GYR["Gyr_Y"]-np.mean(SENSOR_DATA_GYR["Gyr_Y"])) })
SENSOR_DATA_GYR.update({ "Gyr_Z":np.deg2rad(SENSOR_DATA_GYR["Gyr_Z"]-np.mean(SENSOR_DATA_GYR["Gyr_Z"])) })

gyro_random_error_analysis.sensor_data = SENSOR_DATA_GYR

# %%
SENSOR_DATA_ACC = get_data_from_csv("Acc_X","Acc_Y","Acc_Z", file_name="csv_data/Sensors_and_orientation.csv")
acc_random_error_analysis = nav_alg(frequency=100, analysis="dynamic_acc", points_count=len(SENSOR_DATA_ACC["Acc_X"]))
acc_random_error_analysis.set_coordinates(55.75, 37.61)

SENSOR_DATA_ACC.update({ "Acc_X":(SENSOR_DATA_ACC["Acc_X"]-np.mean(SENSOR_DATA_ACC["Acc_X"])) })
SENSOR_DATA_ACC.update({ "Acc_Y":(SENSOR_DATA_ACC["Acc_Y"]-np.mean(SENSOR_DATA_ACC["Acc_Y"])) })
SENSOR_DATA_ACC.update({ "Acc_Z":(SENSOR_DATA_ACC["Acc_Z"]-np.mean(SENSOR_DATA_ACC["Acc_Z"])) })

acc_random_error_analysis.sensor_data = SENSOR_DATA_ACC

#%%
SENSOR_DATA = get_data_from_csv("Acc_X","Acc_Y","Acc_Z", "Gyr_X", "Gyr_Y", "Gyr_Z", file_name="csv_data/Sensors_and_orientation.csv")
random_error_analysis = nav_alg(frequency=100, analysis="dynamic_both", points_count=len(SENSOR_DATA["Acc_X"]))
random_error_analysis.set_coordinates(55.75, 37.61)

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
# %%