#%%
import os
import pandas as pd
import matplotlib.pyplot as plt

log_dir = "/invariant_cube/gyr1"
source_dir = os.path.dirname(os.path.abspath(__file__)) + log_dir
files_list = []
for root, dirs, files in os.walk(source_dir):
    for name in files:
        if name.endswith(("csv")):
            files_list.append(os.path.join(root, name))
files_list.sort()
dfs = []
if __name__ == '__main__':
    for log_file in files_list:
        df = pd.read_csv(log_file, delimiter=';', skiprows=6)
        dfs.append(df)
    
#%%
plt.style.use('fivethirtyeight')
for i in range(len(files_list)):
    dfs[i].plot(
        title=str(i),
        y=["Gyr_X", "Gyr_Y", "Gyr_Z"]
    )
# %%
