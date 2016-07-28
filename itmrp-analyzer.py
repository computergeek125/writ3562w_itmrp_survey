import argparse
import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mpl_colors
import matplotlib.cm as mpl_cm
import pandas as pd
from pprint import pprint
import sys
import textwrap

from qualtrics_api.Qv3 import Qualtrics_v3 as Q
import settings

q = Q(settings.qualtrics_datacenter,settings.qualtrics_api_key)

parser = argparse.ArgumentParser()
parser.add_argument("-R", "--results", help="Sets the results file without re-downloading the results from Qualtrics", default=None)
args = parser.parse_args()

sys.stdout.write("Loading survey from Qualtrics...")
survey = q.survey_get(settings.qualtrics_survey)
sys.stdout.write("done!\n")
if args.results:
    survey_file = args.results
    sys.stdout.write("Reusing results from {0}\n".format(survey_file))
else:
    survey_file = q.response_export(settings.qualtrics_survey,"json")
    sys.stdout.write("Opening {0}\n".format(survey_file))

with open(survey_file) as data_file:    
    survey_data = json.load(data_file)

N = len(survey_data['responses'])
sys.stdout.write("Imported {0} responses\n".format(N))

sys.stdout.write("Survey Name: {0}\n".format(survey['name']))

# Init Matplotlib
mpl.rcParams['backend'] = "TkAgg"

def mc2list(qcol):
    try:
        qid = survey['exportColumnMap'][qcol]['question']
        question = survey['questions'][qid]
    except KeyError:
        raise RuntimeError("{0} is not a multiple choice, single-answer question\n".format(qcol))
    if question['questionType']['type'] == "MC" and question['questionType']['selector'] == "SAVR":
        pass
    elif question['questionType']['type'] == "Matrix" and question['questionType']['subSelector'] == "SingleAnswer":
        matrix=True
    else:
        raise RuntimeError("{0} is not a multiple choice, single-answer type question\n".format(qcol))
        return None
    choices = question['choices']
    rdata_raw = {}
    for i in choices.keys():
        rdata_raw[i] = 0
    for i in survey_data['responses']:
        ans = i[qcol]
        if ans == "":
            pass # Throw out questions they didn't answer
        else:
            rdata_raw[ans] += 1
    #rdata = {}
    #for i in choices.keys():
    #   rdata[choices[i]['choiceText']] = rdata_raw[i]
    bars = []
    names = []
    keys = sorted(rdata_raw.keys(), key=int)
    for i in keys:
        bars += [rdata_raw[i]]
        if not matrix:
            names.append(choices[i]['choiceText'])
        else:
            names.append(choices[i]['description'])
    return {"keys":keys, "bars":bars, "names":names}

def ma2list(qcol): #Compiles the raw respondants from a multiple-choice-multiple-answer question
    qcols = {}
    for i in survey['exportColumnMap'].keys():
        if i.startswith(qcol+"_"):
            if i.endswith("_TEXT"):
                continue
            try:
                qcols[i] = survey['exportColumnMap'][i]['choice'].split(".")
            except KeyError:
                raise RuntimeError("{0} is not a multiple choice-multiple answer question\n".format(qcol))
    qn = sorted(qcols.keys(), key=lambda k: int(qcols[k][2]))
    qid = survey['exportColumnMap'][qn[0]]['question']
    question = survey['questions'][qid]
    if question['questionType']['type'] != "MC" and question['questionType']['selector'] != "MAVR":
        raise RuntimeError("{0} is not a multiple choice-multiple answer question\n".format(qcol))
        return None
    choices = question['choices']
    rdata_raw = {}
    for i in qn:
        rdata_raw[i] = 0
    for i in survey_data['responses']:
        for j in i:
            if j in qn:
                ans = i[j]
                if (ans):
                    rdata_raw[j] += 1
    bars = []
    names = []
    keys = []
    for i in qn:
        bars.append(rdata_raw[i])
        c = qcols[i][2]
        names.append(choices[c]['choiceText'])
        keys.append(c)
    return {"keys":keys, "bars":bars, "names":names}

def list_combine(*lists):
    if len(lists) < 1:
        raise RuntimeError("Input lists must include at least one list")
    bar_len = len(lists[0]['bars'])
    for i in range(1,len(lists)):
        if bar_len != len(lists[i]['bars']):
            raise RuntimeError("Input lists must be the same internal length of the 'bars' dictionary item")
    ret = lists[0]
    rb = lists[0]['bars']
    for i in range(1,len(lists)):
        tl = lists[i]['bars']
        for j in range(len(rb)):
            rb[j] += tl[j]
    ret['bars'] = rb
    return ret

def label_clipper(label, clip): # set clip to negative to bypass this code
    if len(label) > clip and clip > 0:
        label = label[:clip] + "..."
    return label

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
            color = mp_get_cmap(dlen, cmap=cmap)
        else:
            color = [color]*dlen # kluge but it works...
    else:
        color = mp_get_cmap(dlen)
    rects = []
    for i in range(len(data)):
        rects.append(ax.bar(xt+bar_width*i, data[i]["bars"], bar_width, color=color(i), alpha=alpha))

    if xtick_labels:
        names = xtick_labels
    else:
        names = data[0]["names"]
    labels_clipped = [label_clipper(text,label_clip) for text in names]
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
        mp_autolabel(i, ax)

    plt.show(block=False)
    return (fig, ax)

def mcpaired(qcol1, qcol2):
    qid1 = survey['exportColumnMap'][qcol1]['question']
    qid2 = survey['exportColumnMap'][qcol2]['question']
    question1 = survey['questions'][qid1]
    question2 = survey['questions'][qid2]
    if question1['questionType']['type'] != "MC" and question['questionType']['selector'] != "SAVR":
        sys.stderr.write("{0} is not a multiple choice, single-answer question\n".format(qcol1))
        return None
    if question2['questionType']['type'] != "MC" and question['questionType']['selector'] != "SAVR":
        sys.stderr.write("{0} is not a multiple choice, single-answer question\n".format(qcol2))
        return None
    choices1 = question1['choices']
    choices2 = question2['choices']
    pairs = []
    for i in survey_data['responses']:
        ans1 = i[qcol1]
        ans2 = i[qcol2]
        pairs += [(ans1, ans2)]
    names1 = []
    keys1 = sorted(choices1.keys(), key=int)
    for i in keys1:
        names1 += [choices1[i]['choiceText']]
    names2 = []
    keys2 = sorted(choices2.keys(), key=int)
    for i in keys2:
        names2 += [choices2[i]['choiceText']]
    return {"pairs":pairs, "keys1":keys1,"keys2":keys2, "names1":names1,"names2":names2}

def mcmatrix(qcol, exclude_choice=[]):
    qcols = {}
    for i in survey['exportColumnMap'].keys():
        if i.startswith(qcol+"_"):
            if i.endswith("_TEXT"):
                continue
            try:
                qcols[i] = survey['exportColumnMap'][i]['subQuestion'].split(".")
            except KeyError:
                raise RuntimeError("{0} is not a multiple choice matrix question\n".format(qcol))
    qn = sorted(qcols.keys(), key=lambda k: int(qcols[k][2]))
    qid = survey['exportColumnMap'][qn[0]]['question']
    question = survey['questions'][qid]
    if question['questionType']['type'] != "Matrix" and question['questionType']['subSelector'] != "SingleAnswer":
        raise RuntimeError("{0} is not a multiple choice matrix question\n".format(qcol))
        return None
    choices = question['choices']
    sub_questions = question['subQuestions']
    pairs = []
    for i in qn:
        data = mc2list(i)
        bars = data['bars']
        for j in range(len(bars)):
            pairs.append([j+1, int(qcols[i][2]), bars[j]])
    for e in exclude_choice:
        echoice = None
        for c in choices:
            cd = choices[c]['description']
            if cd == e:
                echoice = int(c)
                break
        if not echoice:
            raise RuntimeError("Choice {0} could not be excluded because it doesn't exist...".format(e))
        raise NotImplementedError("TODO")
    names1 = []
    keys1 = sorted(choices.keys(), key=int)
    for i in keys1:
        names1 += [choices[i]['description']]
    names2 = []
    keys2 = sorted(sub_questions.keys(), key=int)
    for i in keys2:
        names2 += [sub_questions[i]['description']]
    return {"pairs":pairs, "keys1":keys1,"keys2":keys2, "names1":names1,"names2":names2}

def scatter_mc(data, c=None, dp=15, title=None, xlabel=None, ylabel=None,
    xlabel_length=15, xlabel_clip=-1, ylabel_length=15, ylabel_clip=-1, xtick_rotation=-45, xtick_labels=None, ytick_labels=None):
    freqs = []
    pairs = []
    for p in data['pairs']:
        found = False
        for i in range(len(freqs)):
            if pairs[i][0] == p[0] and pairs[i][1] == p[1]:
                found = True
                freqs[i] += p[2]
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
    labels1_clipped = [label_clipper(text,xlabel_clip) for text in names1]
    labels1 = [textwrap.fill(text,xlabel_length) for text in labels1_clipped]
    if ytick_labels:
        names2 = ytick_labels
    else:
        names2 = data['names2']
    labels2_clipped = [label_clipper(text,ylabel_clip) for text in names2]
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

#TODO: Text analysis (report) Grab text with selectable metadata, filtering null answers

def mp_autolabel(rects, ax):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.01*height,
                '%d' % int(height),
                ha='center', va='bottom')

def mp_get_cmap(N, cmap='hsv'): # from http://stackoverflow.com/a/25628397/1778122
    '''Returns a function that maps each index in 0, 1, ... N-1 to a distinct 
    RGB color.'''
    color_norm  = mpl_colors.Normalize(vmin=0, vmax=N-1)
    scalar_map = mpl_cm.ScalarMappable(norm=color_norm, cmap=cmap) 
    def map_index_to_rgb_color(index):
        return scalar_map.to_rgba(index)
    return map_index_to_rgb_color

def nars(nars_list): #maybe reimplement using pandas?
    nars_score = []
    for respondant in survey_data['responses']:
        r_vals = []
        #sys.stdout.write("{0}: ".format(respondant['ResponseID']))
        for sq in nars_list:
            ans = respondant[sq]
            #sys.stdout.write("'{0}' ".format(ans))
            if ans == "":
                pass # Throw out questions they didn't answer
            else:
                r_vals.append(int(ans))
        #sys.stdout.write('\n')
        if r_vals:
            r_mean = np.nanmean(r_vals, dtype=np.float64)
            r_std = np.nanstd(r_vals, dtype=np.float64)
        else:
            r_mean = np.NaN
            r_std = np.NaN
        nars_score.append({"ResponseID":respondant['ResponseID'], "mean":r_mean, "std":r_std })
    return nars_score
def nars_inverted(nars_list): # This may or may not work...
    nars_score = []
    for respondant in survey_data['responses']:
        r_vals = []
        #sys.stdout.write("{0}: ".format(respondant['ResponseID']))
        for sq in nars_list:
            ans = respondant[sq]
            #sys.stdout.write("'{0}' ".format(ans))
            if ans == "":
                pass # Throw out questions they didn't answer
            else:
                r_vals.append(likert_invert(int(ans)))
        #sys.stdout.write('\n')
        if r_vals:
            r_mean = np.nanmean(r_vals, dtype=np.float64)
            r_std = np.nanstd(r_vals, dtype=np.float64)
        else:
            r_mean = np.NaN
            r_std = np.NaN
        nars_score.append({"ResponseID":respondant['ResponseID'], "mean":r_mean, "std":r_std })
    return nars_score
def likert_invert(input_num, scale):
    if (scale % 2 == 0):
        raise ValueError("Likert scales must be odd numbers!  You provided a scale of {0}".format(scale))
    if (input_num < 1 or input_num > scale):
        raise ValueError("Likert scale input must be between 1 and {0} inclusive".format(scale))
    return scale - input_num +1
def print_nars(nars_processed):
    for i in nars_processed:
        sys.stdout.write("{0}: m={1} s={2}\n".format(i['ResponseID'], i['mean'], i['std']))