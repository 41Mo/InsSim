import math
import numpy as np
from numba import njit

@njit
def avar(fs, in_data, To=0.01):
    dt = 1.0 / fs
    nsamples = len(in_data)      # number of samples

    tau = np.arange(0.01, 10.0+To, To)
    time = nsamples*dt
    M = time/To
    avar = np.zeros(len(tau))

    for nTo,i in zip(tau,range(0,len(tau))):
        s = 0
        n = math.ceil(nTo/To)
        for m in range(1, int((M-2*n)+1)):
            th_m = np.sum(in_data[0:math.ceil(m*To*fs)])*dt
            th_mn = np.sum(in_data[0:math.ceil((m+n)*To*fs)])*dt
            th_m2n = np.sum(in_data[0:math.ceil((m+2*n)*To*fs)])*dt
            s = s + (th_m2n - 2*th_mn +th_m)**2
        try:
            avar[i] = 1/(2*(M-2*n)*(n*To)**2)*s
        except:
            avar[i] = 0
    return avar, tau