# %%
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '../src/')
from filter import filter
import matplotlib.pyplot as plt
from numpy import newaxis, array, squeeze, linalg, matrix

# %%
files = [
    #"../binary_output/logs3/2.csv",
    # "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/1-1.csv",
    # "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/1-2.csv",
    # "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/1-3.csv",
    # "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/1-4.csv",
    "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/t1.csv",
    "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/t2.csv",
]
imu_frq = 100
gyr = [
    "Gyr_X", "Gyr_Y", "Gyr_Z",
]
acc = [
    "Acc_X", "Acc_Y", "Acc_Z"
]

est_vec = pd.read_csv("../csv_data/calib.csv").to_numpy().squeeze()

t1= linalg.inv(matrix([
    [1+est_vec[3], 0, 0],
    [est_vec[6], 1+est_vec[4],0],
    [est_vec[7], est_vec[8], 1+est_vec[5]]
]))

dr = array([
    est_vec[0],est_vec[1],est_vec[2]
])

# %%
dfs = []
df_cutoff = []
for file in files:
    d = pd.read_csv(file,delimiter=";",skiprows=12)
    t = d.shape[0]/imu_frq/60
    d = d.assign(Time=np.linspace(0, t, d.shape[0]))
    a_v = d.loc[:, acc].to_numpy()

    df_cutoff.append(np.array([5,15]))
    result = []
    for vec in a_v:
        result.append(
            t1@(vec[:,newaxis]-dr[:,newaxis]*9.80665)
        )
    result = array(result)
    result = squeeze(result)


    for a,g,n in zip(acc,gyr,range(3)):
        d[g] = np.rad2deg(d[g])
        d.insert(len(d.columns), a+"_flt", filter(d[a]))
        d.insert(len(d.columns), g+"_flt", filter(d[g]))
        d.insert(len(d.columns), a+"cal_flt",filter(result[:,n]))
    dfs.append(d)

#%%
for t in df_cutoff:
    t *= imu_frq*60

fin_dfs = []
for df, sp in zip(dfs, df_cutoff):
    fin_dfs.append(df.iloc[sp[0]:sp[1]])
# %%
g_s = "Данные гироскопа по оси "
a_s = "Данные акселерометра по оси "
figax= []
for i in range(3):
    figax.append(plt.subplots())

plots = [
    (["Acc_Xcal_flt","Acc_X_flt"], a_s+"X", 'Время,мин', '$\\frac{м}{c^2}$' , ),
    (["Acc_Ycal_flt","Acc_Y_flt"], a_s+"Y", 'Время,мин', '$\\frac{м}{c^2}$' , ),
    (["Acc_Zcal_flt","Acc_Z_flt"], a_s+"Z", 'Время,мин', '$\\frac{м}{c^2}$' , )
]
size = (265/25.4, 152/25.4) # plot size 140, 170 mm
for i in range(2):
    for pl, fa in zip(plots, figax):
        n1="После применения кал. коэф."
        n2="До применения кал. коэф."
        labeled=False
        for df in fin_dfs:
            s=""
            if i == 0:
                line = df.plot(
                x="Time", y=pl[0][i],
                grid=True,
                subplots=False,
                legend=not labeled,
                title=pl[1],
                ylabel=pl[3],
                xlabel=pl[2],
                ax=fa[1],
                linestyle= 'dotted',#(0, (1, 10)),
                figsize=size,
                label=n1,
                )
                labeled=True
            else:
                line = df.plot(
                x="Time", y=pl[0][i],
                grid=True,
                subplots=False,
                legend=not labeled,
                title=pl[1],
                ylabel=pl[3],
                xlabel=pl[2],
                ax=fa[1],
                linestyle='-',
                figsize=size,
                label=n2,
                )
                labeled=True
#%%
plot_names = [
    "calx.jpg",
    "caly.jpg",
    "calz.jpg"
]
path="/home/alex/code_and_everything/nav_alg_workspace/nav_alg/images/"
dpi=500
for pl, n in zip(figax, plot_names):
    pl[0].savefig(path+n, dpi=dpi)

# %%
