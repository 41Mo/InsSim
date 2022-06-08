# %%
import pandas as pd
import numpy as np
from src.filter import filter
import matplotlib.pyplot as plt

# %%
files = [
    #"/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/1-1.csv",
    #"/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/1-2.csv",
    #"/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/1-3.csv"
    # "csv_data/Sensors_and_orientation.csv",
    # "binary_output/logs3/bins-1.csv",
    #"/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/test.csv"
    # "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/invariant_cube/aks1/00g.csv",
    # "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/invariant_cube_1/aks1/00g.csv",
    # "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/t1.csv",
    "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/logs3/t2.csv",
    # "/home/alex/code_and_everything/nav_alg_workspace/nav_alg/binary_output/invariant_cube_1/gyr1/xcw.csv"
]
imu_frq = 100
gyr = [
    "Gyr_X", "Gyr_Y", "Gyr_Z",
]
acc = [
    "Acc_X", "Acc_Y", "Acc_Z"
]

# %%
dfs = []
df_cutoff = []
for file in files:
    d = pd.read_csv(file,delimiter=";",comment='/')
    t = d.shape[0]/imu_frq/60
    d = d.assign(Time=np.linspace(0, t, d.shape[0]))
    df_cutoff.append(np.array([0,2]))
    for a,g in zip(acc,gyr):
        try:
            d[g] = np.rad2deg(d[g])
            d.insert(len(d.columns), g+"_flt", filter(d[g]))
        except KeyError:
            print("Gyros not in file")
        try:
            d.insert(len(d.columns), a+"_flt", filter(d[a]))
        except KeyError:
            print("Acc not in file")
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
for i in range(6):
    figax.append(plt.subplots())

plots = [
    (["Gyr_X","Gyr_X_flt"], g_s+"X", 'Время,мин', '$\\frac{град}{с}$', ),
    (["Gyr_Y","Gyr_Y_flt"], g_s+"Y", 'Время,мин', '$\\frac{град}{с}$', ),
    (["Gyr_Z","Gyr_Z_flt"], g_s+"Z", 'Время,мин', '$\\frac{град}{с}$', ),
    (["Acc_X","Acc_X_flt"], a_s+"X", 'Время,мин', '$\\frac{м}{c^2}$' , ),
    (["Acc_Y","Acc_Y_flt"], a_s+"Y", 'Время,мин', '$\\frac{м}{c^2}$' , ),
    (["Acc_Z","Acc_Z_flt"], a_s+"Z", 'Время,мин', '$\\frac{м}{c^2}$' , )
]
size = (244/25.4, 94/25.4) # plot size 140, 170 mm
for i in range(2):
    for pl, fa in zip(plots, figax):
        for df in fin_dfs:
            s=""
            try:
                df.plot(
                x="Time", y=pl[0][i],
                grid=True,
                subplots=False,
                #legend=False,
                title=pl[1],
                ylabel=pl[3],
                xlabel=pl[2],
                ax=fa[1],
                figsize=size,
                )
                if i == 0:
                    s+=f"Std {pl[0][0]}: {np.std(df[pl[0][0]]):7.5f}\n"
                    print(s)
            except KeyError:
                pass

# %%

plot_names = [
    "Gstatx.jpg",
    "Gstaty.jpg",
    "Gstatz.jpg",
    "Astatx.jpg",
    "Astaty.jpg",
    "Astatz.jpg",
]
path="/home/alex/code_and_everything/nav_alg_workspace/nav_alg/images/"
dpi=500
for pl, n in zip(figax, plot_names):
    pl[0].savefig(path+n, dpi=dpi)
# %%
mag = pd.read_csv("csv_data/MAGFIELD.csv",delimiter=";")
t = mag.shape[0]/imu_frq/60
mag = mag.assign(Time=np.linspace(0, t, mag.shape[0]))
yaw = np.arctan2(mag["Mag_X"],mag["Mag_Y"])

#np.rad2deg((abs(yaw[len(yaw)-1])) - np.deg2rad(abs(mag["Yaw"][len(mag["Yaw"])-1])))
heading_calc=[]
for e in yaw:
    if e<0:
        heading_calc.append(e+2*np.pi)
    else:
        heading_calc.append(e)
#heading_calc = filter(heading_calc, T=0.1)

heading=[]
for e in mag["Yaw"]:
    if e<0:
        heading.append(e+np.rad2deg(2*np.pi))
    else:
        heading.append(e)
#heading = filter(heading, T=0.5)
#yaw = filter(yaw,T=0.1)
mag = mag.assign(yaw_calc=np.rad2deg(yaw))
mag = mag.assign(heading_calc=np.rad2deg(heading_calc))
mag = mag.assign(heading=heading)
mag.plot(x="Time", y=["Mag_X", "Mag_Y"], xlabel="время, мин", ylabel="B, Тл")
plt.savefig("images/mag_mag.jpg",dpi=500)
mag.plot(x="Time",y=["Yaw", "yaw_calc"],  label=["рыскание полученное", "рыскание рассчитанное"], xlabel="время, мин", ylabel="град")
#mag.plot(x="Time",y=["heading", "heading_calc"], label=["курс полученный", "курс рассчитанный"])
plt.savefig("images/mag_yaw.jpg",dpi=500)
# %%