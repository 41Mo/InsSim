#%%
import numpy as np

dt = 1

wbx =0; wby =0; wbz =0;
wox = 0; woy = 0.000726; woz=0;

w_body = np.array([
    [   0, -wbz,  wby],
    [ wbz,    0, -wbx],
    [-wby,  wbx,    0]
], dtype=np.double)

w_enu = np.array([
    [   0, -woz,  woy],
    [ woz,    0, -wox],
    [-woy,  wox,    0]
], dtype=np.double)

C = np.eye(3, 3)

C = C + (C @ w_body  - w_enu @ C) * dt