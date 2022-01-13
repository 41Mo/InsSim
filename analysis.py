#%%
import numpy as np
import math as math
from importlib import reload  # Python 3.4+

import src.nav_alg
src.nav_alg = reload(src.nav_alg)
from src.nav_alg import nav_alg
from src.csv_parser import get_data_from_csv

import logging
logging.basicConfig(
    format='%(module)s:%(levelname)s:%(message)s',
    filename='logs/Run.log',
    filemode="w",
    encoding='utf-8',
    level=logging.WARNING)
logging.getLogger('src.nav_alg').setLevel(logging.INFO)

#%%
# e.g Moscow
lat = 0#55.75
lon = 0#37.61

# file with real sensors data
data_file = "csv_data/Sensors_and_orientation.csv"
sample_time = 1800
data_frequency = 100
save_plots = False # plots would be saved to images folder
plots_size = (297,210) # plots height,width in mm
# additional plots such as wx,wy,wz,ax,ay,az in both body and enu would be shown
show_additional_plots = True

# sensor errors
acc_offset = 0.0001 # 2 [mg]
gyr_drift = math.radians(10)/3600 # [deg/hour]

#%%
# alignemnt errors [deg]
# 0 - assuming no errors
psi = 0
teta = 0
gamma = 0

# %%
ideal_system = nav_alg()

acc_offset_analysis = nav_alg(obj_name="смещение 0 акселерометров")
acc_offset_analysis.set_a_body(
    acc_offset,
    acc_offset,
    0#acc_offset
)
acc_offset_analysis.set_coordinates(lat, lon)

gyro_drift_analysis= nav_alg(obj_name="дрейф гироскопов")
gyro_drift_analysis.set_w_body(
    gyr_drift,
    gyr_drift,
    0#gyr_drift
)
gyro_drift_analysis.set_coordinates(lat, lon)

#%%
SENSOR_DATA = get_data_from_csv("Gyr_X","Gyr_Y","Gyr_Z","Acc_X","Acc_Y","Acc_Z", file_name=data_file)

#%%
gyro_random_error_analysis = nav_alg(analysis="dynamic_gyro", time=sample_time, frequency=data_frequency, obj_name="случайная ошибка гироскопов")
gyro_random_error_analysis.set_coordinates(lat, lon)

SENSOR_DATA_GYR = SENSOR_DATA
SENSOR_DATA_GYR.update({ "Gyr_X":np.deg2rad(SENSOR_DATA_GYR["Gyr_X"]-np.mean(SENSOR_DATA_GYR["Gyr_X"])) })
SENSOR_DATA_GYR.update({ "Gyr_Y":np.deg2rad(SENSOR_DATA_GYR["Gyr_Y"]-np.mean(SENSOR_DATA_GYR["Gyr_Y"])) })
SENSOR_DATA_GYR.update({ "Gyr_Z":np.deg2rad(SENSOR_DATA_GYR["Gyr_Z"]-np.mean(SENSOR_DATA_GYR["Gyr_Z"])) })

gyro_random_error_analysis.sensor_data = SENSOR_DATA_GYR

# %%
acc_random_error_analysis = nav_alg(analysis="dynamic_acc", time=sample_time, frequency=data_frequency, obj_name="случайная ошибка акселерометров")
acc_random_error_analysis.set_coordinates(lat, lon)

SENSOR_DATA_ACC = SENSOR_DATA
SENSOR_DATA_ACC.update({ "Acc_X":(SENSOR_DATA_ACC["Acc_X"]-np.mean(SENSOR_DATA_ACC["Acc_X"])) })
SENSOR_DATA_ACC.update({ "Acc_Y":(SENSOR_DATA_ACC["Acc_Y"]-np.mean(SENSOR_DATA_ACC["Acc_Y"])) })
SENSOR_DATA_ACC.update({ "Acc_Z":(SENSOR_DATA_ACC["Acc_Z"]-np.mean(SENSOR_DATA_ACC["Acc_Z"])) })

acc_random_error_analysis.sensor_data = SENSOR_DATA_ACC

# %%
import threading
    
def create_threads_and_run(*objects):
    threads = []
    for object in objects:
        threads.append(threading.Thread(target=object.analysis))
    
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    for object in objects:
        object.plots(size=plots_size, save=save_plots, additional_plots=show_additional_plots)


create_threads_and_run(
    #acc_offset_analysis,
    #gyro_drift_analysis,
    #gyro_random_error_analysis,
    acc_random_error_analysis,
    #ideal_system
    )

# %% Manual plot building
#ideal_system.plots(save=False, title="ideal")
#acc_offset_analysis.plots(save=False, title="acc_offset")
#gyro_drift_analysis.plots(save=False, title="gyro drift")
#gyro_random_error_analysis.plots(save=False, title="gyr rnd")
#acc_random_error_analysis.plots(save=False, title="acc rnd")

# %%