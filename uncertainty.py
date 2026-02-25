import numpy as np

def uncertainty_range(values):
    mean = np.mean(values)
    low = mean * 0.9
    high = mean * 1.1
    return low, high