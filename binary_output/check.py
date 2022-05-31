#%%
import os
import pandas as pd
import matplotlib.pyplot as plt

log_dir = "/invariant_cube_1/gyr1"
source_dir = os.path.dirname(os.path.abspath(__file__)) + log_dir
files_list = []
names_list = []
for root, dirs, files in os.walk(source_dir):
    for name in files:
        if name.endswith(("csv")):
            names_list.append(name)
            files_list.append(os.path.join(root, name))
#files_list.sort()
dfs = []
if __name__ == '__main__':
    for log_file in files_list:
        df = pd.read_csv(log_file, delimiter=';', skiprows=5)
        dfs.append(df)
    
#%%
plt.style.use('fivethirtyeight')
data = ["Gyr_X", "Gyr_Y", "Gyr_Z"]
#data = ["Acc_X", "Acc_Y", "Acc_Z"]
for df, title in zip(dfs, names_list):
    df.plot(
        title=title,
        y=data
    )
# %%
