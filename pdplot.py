import matplotlib
import matplotlib.pyplot as plt

def pdplot(pddata, kind='bar', xlabel=None, ylabel=None, xbound=[None, None], ybound=[None, None], title=None, **kwargs):
    ax = pddata.plot(kind=kind, **kwargs)
    #plt.axhline(0, color='k')
    if xbound:
        if xbound[0]:
            ax.set_xbound(lower=xbound[0])
        if xbound[1]:
            ax.set_xbound(upper=xbound[1])
    if ybound:
        if ybound[0]:
            ax.set_ybound(lower=ybound[0])
        if ybound[1]:
            ax.set_ybound(upper=ybound[1])
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize="xx-large", y=1.04)
    return ax