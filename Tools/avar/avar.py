import math
import numpy as np
from functools import partial
from multiprocessing import Pool, freeze_support
import time

import os

def calulation_loop(tau, in_data, To, M, fs, dt):
    nTo = tau
    s = 0
    n = math.ceil(nTo/To)
    if n >= (M-1)/2:
        return 0
    for m in range(1, int((M-2*n))):
        th_m = np.sum(in_data[0:math.ceil(m*To*fs)])*dt
        th_mn = np.sum(in_data[0:math.ceil((m+n)*To*fs)])*dt
        th_m2n = np.sum(in_data[0:math.ceil((m+2*n)*To*fs)])*dt
        s = s + (th_m2n - 2*th_mn +th_m)**2

    return 1/(2*(M-2*n)*(n*To)**2)*s

def avar(fs, in_data, To=0.01):
    dt = 1.0 / fs
    nsamples = len(in_data)      # number of samples

    tau = np.arange(0.01, 10.0+To, To)
    time = nsamples*dt
    M = time/To
    avar = []

    freeze_support()
    cc = os.cpu_count()

    with Pool(processes=cc) as pool:
        tst = partial(calulation_loop, in_data=in_data.copy(), To=To, M=M, fs=fs, dt=dt)
        avar = pool.map(tst, tau)

    return avar, tau