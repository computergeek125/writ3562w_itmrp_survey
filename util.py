import os
import numpy as np
import pandas as pd

def reload_window():
    rows, cols = os.popen('stty size', 'r').read().split()
    rows = int(rows)
    cols = int(cols)
    pd.set_option('display.width',cols)

def likert_mean(indata, lsize=5):                         
     d = np.arange(1,lsize+1)                                                                 
     return np.average(d, weights=indata)

def likert_ms(indata, lsize=5):                         
     d = np.arange(1,lsize+1)                                                                 
     return weighted_avg_and_std(d, indata)

def weighted_avg_and_std(values, weights):
    """
    From: http://stackoverflow.com/a/2415343/1778122
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)  # Fast and numerically precise
    return (average, np.sqrt(variance))