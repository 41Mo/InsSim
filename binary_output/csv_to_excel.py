#%%
import os
import pandas as pd

sensors = ["aks1", "gyr1"]
save_dir = "/excel_dump_old"
for s in sensors:
    log_dir = "/invariant_cube/"+s
    source_dir = os.path.dirname(os.path.abspath(__file__)) + log_dir
    files_list = []
    names_list = []
    try:
        for root, dirs, files in os.walk(source_dir):
            for name in files:
                if name.endswith(("csv")):
                    files_list.append(os.path.join(root, name))
                    names_list.append(name.split(".")[0])
    except:
        print("error finding dir")
    excel_dump_path=os.path.dirname(os.path.abspath(__file__))+save_dir
    ext = ".xlsx"
    for log_file,name in zip(files_list,names_list):
        df = pd.read_csv(log_file, delimiter=';', skiprows=5)
        df.to_excel(excel_dump_path+"/"+name+ext)
# %%
