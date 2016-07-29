import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys
import textwrap

import plotting_util as u

# Init Matplotlib
mpl.rcParams['backend'] = "TkAgg"

def barchart(data, legend=[], label_length=15, label_clip=-1, title=None, xlabel=None, ylabel=None, 
    xtick_rotation=-45, xtick_labels=None, group_width=0.7, color=None, alpha=0.5):
    # data should be a list of lists: each sub-list is a series in the data, and each item in the sublists is a bar
    # based on: http://matplotlib.org/examples/api/barchart_demo.html
    fig, ax = plt.subplots()
    try:
        a = data[0][0]
    except TypeError:
        data = [data]
    pN = len(data[0])
    dlen = len(data)
    bar_width = group_width/dlen
    xt = np.arange(pN)  # the x locations for the groups
    if color:
        if type(color) is tuple or type(color) is list:
            if len(color) < dlen:
                raise RuntimeError("If you specify a list of colors, the length must match the number of series in data")
        elif type(color) is str:
            cmap = color
            color = u.mp_get_cmap(dlen, cmap=cmap)
        else:
            color = [color]*dlen # kluge but it works...
    else:
        color = u.mp_get_cmap(dlen)
    rects = []
    for i in range(len(data)):
        rects.append(ax.bar(xt+bar_width*i, data[i], bar_width, color=color(i), alpha=alpha))

    # add some text for labels, title and axes ticks
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize="xx-large", y=1.04)
    
    mb = None
    for i in data:
        lm = max(i)
        if mb is None:
            mb = lm
        elif lm > mb:
            mb = lm
    ax.set_xbound(lower=xt[0]+group_width/2-0.5, upper=xt[-1]+group_width/2+0.5)
    ax.set_ybound(upper=mb*1.07)
    ax.set_xticks(xt + group_width/2)
    ax.autoscale(enable=False, axis="x", tight=True)

    if xtick_labels:
        names = xtick_labels
        labels_clipped = [u.label_clipper(text,label_clip) for text in names]
        labels = [textwrap.fill(text,label_length) for text in labels_clipped]
        bot_off = (-np.sin(np.radians(xtick_rotation))) * (label_length * 0.016)
        fig.subplots_adjust(bottom=bot_off)
    else:
        labels = [""]*dlen
    ax.set_xticklabels(labels, rotation=xtick_rotation)

    if dlen > 1:
        lr = []
        for i in rects:
            lr.append(i[0])
        llen = len(legend)
        if llen < dlen:
            for i in range(llen-1, dlen):
                legend.append("Series {0}".format(i+1))
        lmax = 0
        for i in legend:
            li = len(i)
            if li > lmax:
                lmax = li
        ax.legend(lr, legend, bbox_to_anchor=(1,1), bbox_transform=fig.transFigure)
        fig.subplots_adjust(left=0.05, right=1-(0.016*li+0.05))
    
    for i in rects:
        u.mp_autolabel(i, ax)

    plt.show(block=False)
    return (fig, ax)

def plot_mc(data, legend=[], label_length=15, label_clip=-1, title=None, xlabel=None, ylabel=None, 
    xtick_rotation=-45, xtick_labels=None, group_width=0.7, color=None, alpha=0.5):
    # data should be of format: {'keys': ['1', '2', '3', '4', '5'], 'names': ['One', 'Two', 'Three', 'Four', 'Five'], 'bars': [5, 13, 1, 1, 0]}
    # based on: http://matplotlib.org/examples/api/barchart_demo.html
    fig, ax = plt.subplots()
    if type(data) is tuple or type(data) is list:
        pass
    else:
        data = [data]
    pN = len(data[0]["bars"])
    dlen = len(data)
    bar_width = group_width/dlen
    xt = np.arange(pN)  # the x locations for the groups
    if color:
        if type(color) is tuple or type(color) is list:
            if len(color) < dlen:
                raise RuntimeError("If you specify a list of colors, the length must match the number of series in data")
        elif type(color) is str:
            cmap = color
            color = u.mp_get_cmap(dlen, cmap=cmap)
        else:
            color = [color]*dlen # kluge but it works...
    else:
        color = u.mp_get_cmap(dlen)
    rects = []
    for i in range(len(data)):
        rects.append(ax.bar(xt+bar_width*i, data[i]["bars"], bar_width, color=color(i), alpha=alpha))

    if xtick_labels:
        names = xtick_labels
    else:
        names = data[0]["names"]
    labels_clipped = [u.label_clipper(text,label_clip) for text in names]
    labels = [textwrap.fill(text,label_length) for text in labels_clipped]


    # add some text for labels, title and axes ticks
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize="xx-large", y=1.04)
    ax.set_xticks(xt + group_width/2)
    ax.set_xbound(lower=xt[0]+group_width/2-0.5, upper=xt[-1]+group_width/2+0.5)
    mb = None
    for i in data:
        lm = max(i['bars'])
        if mb is None:
            mb = lm
        elif lm > mb:
            mb = lm
    ax.set_ybound(upper=mb*1.07)
    ax.set_xticklabels(labels, rotation=xtick_rotation)
    ax.autoscale(enable=False, axis="x", tight=True)
    bot_off = (-np.sin(np.radians(xtick_rotation))) * (label_length * 0.016)
    fig.subplots_adjust(bottom=bot_off)

    if dlen > 1:
        lr = []
        for i in rects:
            lr.append(i[0])
        llen = len(legend)
        if llen < dlen:
            for i in range(llen-1, dlen):
                legend.append("Series {0}".format(i+1))
        lmax = 0
        for i in legend:
            li = len(i)
            if li > lmax:
                lmax = li
        ax.legend(lr, legend, bbox_to_anchor=(1,1), bbox_transform=fig.transFigure)
        fig.subplots_adjust(left=0.05, right=1-(0.016*li+0.05))
    
    for i in rects:
        u.mp_autolabel(i, ax)

    plt.show(block=False)
    return (fig, ax)

def scatter_mc(data, c=None, dp=15, title=None, xlabel=None, ylabel=None,
    xlabel_length=15, xlabel_clip=-1, ylabel_length=10, ylabel_clip=-1, xtick_rotation=-45, xtick_labels=None, ytick_labels=None):
    freqs = []
    pairs = []
    for p in data['pairs']:
        found = False
        for i in range(len(freqs)):
            if pairs[i][0] == p[0] and pairs[i][1] == p[1]:
                found = True
                if len(p) > 2:
                    freqs[i] += p[2]
                else:
                    freqs[i] += 1
                break
        if not found:
            pairs.append((p[0],p[1]))
            if len(p) > 2:
                freqs.append(p[2])
            else:
                freqs.append(1)
    x,y = zip(*pairs)
    area = np.pi * (dp * np.array(freqs))**2
    fig, ax = plt.subplots()
    xt = list(map(int,data["keys1"]))
    yt = list(map(int,data["keys2"]))
    ax.set_xticks(xt)
    ax.set_yticks(yt)
    ax.set_xbound(lower=xt[0]-0.5, upper=xt[-1]+0.5)
    ax.set_ybound(lower=yt[0]-0.5, upper=yt[-1]+0.5)
    if xtick_labels:
        names1 = xtick_labels
    else:
        names1 = data['names1']
    labels1_clipped = [u.label_clipper(text,xlabel_clip) for text in names1]
    labels1 = [textwrap.fill(text,xlabel_length) for text in labels1_clipped]
    if ytick_labels:
        names2 = ytick_labels
    else:
        names2 = data['names2']
    labels2_clipped = [u.label_clipper(text,ylabel_clip) for text in names2]
    labels2 = [textwrap.fill(text,ylabel_length) for text in labels2_clipped]
    ax.set_xticklabels(labels1)
    ax.set_yticklabels(labels2)
    ax.autoscale(enable=False, axis="both", tight=True)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
        plt.subplots_adjust(left=0.15)
    if title:
        ax.set_title(title)
    xy = list(zip(x,y))
    for l in range(len(xy)):
        if freqs[l] > 0:
            plt.annotate(freqs[l], xy = xy[l], xytext = (-4, -4), textcoords = 'offset points')
    plt.scatter(x, y, c=c, s=area, alpha=0.5)
    plt.show(block=False)