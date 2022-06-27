#%%
import subprocess
import pandas as pd
def exec_script(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate() 
    result = out.decode("utf-8").splitlines()
    return result

#%%
r1_file = "../tmp/r1.csv"
cmd = f'/mnt/DATA/kurs/bin/python invariant_cal.py\
 --iter_n 6\
 --out {r1_file}\
 ../binary_output/invariant_cube/aks1'
print(exec_script(cmd))
r3_file = "../tmp/r3.csv"
cmd = f'/mnt/DATA/kurs/bin/python invariant_cal.py\
 --iter_n 6\
 --out {r3_file}\
 ../binary_output/invariant_cube_1/aks1'
print(exec_script(cmd))
p1 = pd.read_csv(r1_file)
p3 = pd.read_csv(r3_file)
r = pd.concat([p1, p3])
r
#r.to_excel("../tmp/r.xlsx", index=False)

#%%
e_f = "../tmp/r3.csv"
r1_file = "../tmp/t1.csv"
cmd = f'/mnt/DATA/kurs/bin/python invariant_cal.py\
 --iter_n 2\
 --out {r1_file}\
 --est_file={e_f}\
 ../binary_output/invariant_cube/aks1'
print(exec_script(cmd))
r3_file = "../tmp/t3.csv"
cmd = f'/mnt/DATA/kurs/bin/python invariant_cal.py\
 --iter_n 6\
 --out {r3_file}\
 --est_file={e_f}\
 ../binary_output/invariant_cube_1/aks1'
print(exec_script(cmd))
p1 = pd.read_csv(r1_file)
p3 = pd.read_csv(r3_file)
pd.concat([p1, p3])