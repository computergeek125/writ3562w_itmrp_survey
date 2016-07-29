import matplotlib
import matplotlib.pyplot as plt

def pdplot(pddata, kind='bar', xlabel=None, ylabel=None, title=None, **kwargs):
    ax = pddata.plot(kind=kind, **kwargs)
    plt.axhline(0, color='k')
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize="xx-large", y=1.04)

