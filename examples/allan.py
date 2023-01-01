#%%
from Tools.avar.avar import avar
import numpy as np
import matplotlib.pyplot as plt

freq = 10000
time = np.linspace(0,1,freq)
arg = 2*np.pi*5*time
sinwave = 0.01*np.sin(arg)
plt.plot(time, sinwave)

#%%
allan_dispersion, tau = avar(freq,sinwave, 0.001)
#%%
allan_deviation=np.sqrt(allan_dispersion)
plt.plot(tau, allan_deviation)
plt.xscale('log')
plt.yscale('log')
#%%
print(
    "Amplitude: ", 
    np.round(np.max(allan_deviation)/0.725, 3), " rad/s ",
    "Frequency: ",
    np.round(0.371/(tau[np.argmax(allan_deviation)]),0), " Hz"
)
#%%