#%%
from math import sqrt
from numpy.random import normal as rndnorm
def gen_colour_noize(std, Tk, sample_time, data_frequency):
    mean = 0
    norm_std = 1
    num_samples = sample_time*data_frequency
    tau = 1/data_frequency
    samples = rndnorm(mean, norm_std, size=num_samples)
    W = [0]
    for i in range(0, num_samples-1):
        W.append( (1 - tau/Tk) * W[i] + std * sqrt(2*tau/Tk)*samples[i] )
    

    return W

# test
