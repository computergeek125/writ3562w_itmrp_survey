import matplotlib.colors as mpl_colors
import matplotlib.cm as mpl_cm
import sys
import textwrap

def label_clipper(label, clip): # set clip to negative to bypass this code
    if len(label) > clip and clip > 0:
        label = label[:clip] + "..."
    return label

def mp_autolabel(rects, ax):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        if type(height) is int:
        	fs = '{0}'
        else:
        	fs = "{0:.2f}"
        ax.text(rect.get_x() + rect.get_width()/2., 1.01*height,
                fs.format(height),
                ha='center', va='bottom')

def mp_get_cmap(N, cmap='hsv'): # from http://stackoverflow.com/a/25628397/1778122
    '''Returns a function that maps each index in 0, 1, ... N-1 to a distinct 
    RGB color.'''
    color_norm  = mpl_colors.Normalize(vmin=0, vmax=N-1)
    scalar_map = mpl_cm.ScalarMappable(norm=color_norm, cmap=cmap) 
    def map_index_to_rgb_color(index):
        return scalar_map.to_rgba(index)
    return map_index_to_rgb_color