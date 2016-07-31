import matplotlib
import matplotlib.pyplot as plt
import textwrap

import plotting_util as u

def pdplot(pddata, kind='bar', title=None, xlabel=None, ylabel=None, legend=[],
    xrot=-45, xtick_labels=None, label_length=15, label_clip=-1,
    xbound=[None, None], ybound=[None, None],  **kwargs):
    kwargs['rot'] = xrot
    #if type(data) is tuple or type(data) is list:
    #    pass
    #else:
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


    if xtick_labels:
        names = xtick_labels
    else:
        names = pddata.index
    labels_clipped = [u.label_clipper(text,label_clip) for text in names]
    labels = [textwrap.fill(text,label_length) for text in labels_clipped]
    ax.set_xticklabels(labels)

    if legend:
        ax.legend(legend, loc='best')
    return ax

def nars_graphby(nars, nars_s1, nars_s2, nars_s3, question, **kwargs):
    na = nars.nars_associate(nars_s1, nars_s2, nars_s3, [question])
    nam = nars.nars_associate_mean(na, question)
    na_means = nam.loc[['nars_s1_mean','nars_s2_mean','nars_s3_mean']]
    na_err = nam.loc[['nars_s1_std','nars_s2_std','nars_s3_std']]
    na_means.index = ["NARS S1", "NARS S2", "NARS S3"]
    na_err.index = ["NARS S1", "NARS S2", "NARS S3"]
    ax = pdplot(na_means, **kwargs, yerr=na_err)
    return ax