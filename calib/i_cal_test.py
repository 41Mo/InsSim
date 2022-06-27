import pandas as pd
from numpy import linalg, array, matrix
#%% compensation test
X = pd.read_csv("../tmp/r1.csv").to_numpy().squeeze()
dfn = pd.read_csv('../csv_data/Sensors_and_orientation.csv', delimiter=';',skiprows=12)

t1= linalg.inv(matrix([
    [1+X[3], 0, 0],
    [X[6], 1+X[4],0],
    [X[7], X[8], 1+X[5]]
]))

dr = array([
    X[0],X[1],X[2]
])

a = dfn.loc[:, ["Acc_X", "Acc_Y", "Acc_Z"]].to_numpy()
#%%
points = len(a)
frq = 100
time = points/frq
time_axis = linspace(0, time, points)

for i in range(2):
    print("Было ax, ay, az")
    print((a[0])[:,newaxis])
    print("Стало ax, ay, az")
    print( t1@((a[0])[:,newaxis]-dr[:,newaxis]*g) )

result = []
for vec in a:
    result.append(
        t1@(vec[:,newaxis]-dr[:,newaxis]*g)
    )
result = array(result)
result = squeeze(result)
#%%
T=10
slice_from = 15000
res_df = pd.DataFrame({
    "Time":time_axis[slice_from:],
    "AccX_before_cal":(a[:,0])[slice_from:],
    "AccY_before_cal":(a[:,1])[slice_from:],
    "AccZ_before_cal":(a[:,2])[slice_from:],
    "AccX_after_cal": (result[:,0])[slice_from:],
    "AccY_after_cal": (result[:,1])[slice_from:],
    "AccZ_after_cal": (result[:,2])[slice_from:],
    "AccX_before_cal_f": filter(a[:,0], T=T)[slice_from:],
    "AccY_before_cal_f": filter(a[:,1], T=T)[slice_from:],
    "AccZ_before_cal_f": filter(a[:,2], T=T)[slice_from:],
    "AccX_after_cal_f": filter(result[:,0], T=T)[slice_from:],
    "AccY_after_cal_f": filter(result[:,1], T=T)[slice_from:],
    "AccZ_after_cal_f": filter(result[:,2], T=T)[slice_from:],
})
#%%
size = (140*2/25.4, 170*2/25.4)
plt.style.use('fivethirtyeight')
dump = res_df.plot(
    x="Time",
    subplots=True,
    layout=[3,2],
    figsize=size,
    y=[
        "AccX_before_cal", "AccX_after_cal",
        "AccY_before_cal", "AccY_after_cal",
        "AccZ_before_cal", "AccZ_after_cal",
    ]
)
#%%
size = (400/25.4, 170/25.4)
dump = res_df.plot(
    x="Time",
    figsize=size,
    y=[
        "AccX_before_cal_f", "AccX_after_cal_f",
        "AccY_before_cal_f", "AccY_after_cal_f",
    ]
)

dump = res_df.plot(
    x="Time",
    figsize=size,
    y=[
        "AccZ_before_cal_f", "AccZ_after_cal_f",
    ]
)

# %%