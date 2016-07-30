import os
import pandas as pd

def reload_window():
    rows, cols = os.popen('stty size', 'r').read().split()
    rows = int(rows)
    cols = int(cols)
    pd.set_option('display.width',cols)