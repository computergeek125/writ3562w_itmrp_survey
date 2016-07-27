import argparse
import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas
from pprint import pprint
import sys
import textwrap

from qualtrics_api.Qv3 import Qualtrics_v3 as Q
import settings

q = Q(settings.qualtrics_datacenter,settings.qualtrics_api_key)

parser = argparse.ArgumentParser()
parser.add_argument("-R", "--results", help="Sets the results file without re-downloading the results from Qualtrics", default=None)
args = parser.parse_args()

survey = q.survey_get(settings.qualtrics_survey)
if args.results:
    survey_file = args.results
    sys.stdout.write("Reusing results from {0}\n".format(survey_file))
else:
    survey_file = q.response_export(settings.qualtrics_survey,"json")
    sys.stdout.write("Opening {0}\n".format(survey_file))

with open(survey_file) as data_file:    
    survey_data = json.load(data_file)

N = len(survey_data['responses'])
print("Imported {0} responses".format(N))

sys.stdout.write("Survey Name: {0}\n".format(survey['name']))

# Init Matplotlib
mpl.rcParams['backend'] = "TkAgg"

def mc2list(qcol):
    try:
        qid = survey['exportColumnMap'][qcol]['question']
        question = survey['questions'][qid]
    except KeyError:
        raise RuntimeError("{0} is not a multiple choice, single-answer question\n".format(qcol))
    if question['questionType']['type'] != "MC" and question['questionType']['selector'] != "SAVR":
        raise RuntimeError("{0} is not a multiple choice, single-answer question\n".format(qcol))
        return None
    choices = question['choices']
    rdata_raw = {}
    for i in choices.keys():
        rdata_raw[i] = 0
    for i in survey_data['responses']:
        ans = i[qcol]
        #print(ans)
        rdata_raw[ans] += 1
    #rdata = {}
    #for i in choices.keys():
    #   rdata[choices[i]['choiceText']] = rdata_raw[i]
    bars = []
    names = []
    kl = list(rdata_raw.keys())
    kl.sort(key=int)
    keys = kl
    for i in keys:
        bars += [rdata_raw[i]]
        names += [choices[i]['choiceText']]
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
                #print(j)
                ans = i[j]
                #print(ans)
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
    labels_clipped = [label_clipper(text,label_clip) for text in names]
    labels = [textwrap.fill(text,label_length) for text in labels_clipped]
    return {"keys":keys, "bars":bars, "names":names, "labels":labels}

def label_clipper(label, clip): # set clip to negative to bypass this code
    if len(label) > clip and clip > 0:
        label = label[:clip] + "..."
    return label

def plot_mc(data, label_length=15, label_clip=-1, title=None, xlabel=None, ylabel=None, xtick_rotation=-45, xtick_labels=None, bar_width=0.4, color='g', alpha=0.5):
    # data should be of format: {'keys': ['1', '2', '3', '4', '5'], 'names': ['One', 'Two', 'Three', 'Four', 'Five'], 'bars': [5, 13, 1, 1, 0]}
    # based on: http://matplotlib.org/examples/api/barchart_demo.html
    pN = len(data["bars"])
    xt = np.arange(pN)  # the x locations for the groups

    fig, ax = plt.subplots()
    rects1 = ax.bar(xt, data["bars"], bar_width, color=color, alpha=alpha)
    if xtick_labels:
        names = xtick_labels
    else:
        names = data["labels"]
    labels_clipped = [label_clipper(text,label_clip) for text in names]
    labels = [textwrap.fill(text,label_length) for text in labels_clipped]

    # add some text for labels, title and axes ticks
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize="xx-large", y=1.04)
    ax.set_xticks(xt + bar_width/2)
    ax.set_xbound(lower=xt[0]+bar_width/2-0.5, upper=xt[-1]+bar_width/2+0.5)
    mb = max(data['bars'])
    ax.set_ybound(upper=mb*1.07)
    ax.set_xticklabels(labels, rotation=xtick_rotation)
    ax.autoscale(enable=False, axis="x", tight=True)
    bot_off = (-np.sin(np.radians(xtick_rotation))) * (label_length * 0.016)
    fig.subplots_adjust(bottom=bot_off)

    #ax.legend((rects1[0], rects2[0]), ('Men', 'Women'))
    
    mp_autolabel(rects1, ax)
    #autolabel(rects2)

    plt.show(block=False)
    return (fig, ax)

def mcpaired(qcol1, qcol2):
    qid1 = survey['exportColumnMap'][qcol1]['question']
    qid2 = survey['exportColumnMap'][qcol2]['question']
    question1 = survey['questions'][qid1]
    question2 = survey['questions'][qid2]
    if question1['questionType']['type'] != "MC":
        sys.stderr.write("{0} is not a multiple choice question\n".format(qcol1))
        return None
    if question2['questionType']['type'] != "MC":
        sys.stderr.write("{0} is not a multiple choice question\n".format(qcol2))
        return None
    choices1 = question1['choices']
    choices2 = question2['choices']
    pairs = []
    for i in survey_data['responses']:
        ans1 = i[qcol1]
        ans2 = i[qcol2]
        pairs += [(ans1, ans2)]
    names1 = []
    kl1 = list(choices1.keys())
    kl1.sort(key=int)
    keys1 = kl1
    for i in keys1:
        names1 += [choices1[i]['choiceText']]
    if len(names1) == len(keys1)-1:
        names1 += ['Other']
    labels1=[textwrap.fill(text,15) for text in names1]
    names2 = []
    kl2 = list(choices2.keys())
    kl2.sort(key=int)
    keys2 = kl2
    for i in keys2:
        names2 += [choices2[i]['choiceText']]
    if len(names2) == len(keys2)-1:
        names2 += ['Other']
    labels2=[textwrap.fill(text,10) for text in names2]
    return {"pairs":pairs, "keys1":keys1,"keys2":keys2, "names1":names1,"names2":names2, "labels1":labels1,"labels2":labels2}

def scatter_mc(qcol1, qcol2, c=None, title=None, xlabel=None, ylabel=None, dp=15):
    data = mcpaired(qcol1, qcol2)
    freqs = []
    pairs = []
    for p in data['pairs']:
        found = False
        for i in range(len(freqs)):
            if pairs[i][0] == p[0] and pairs[i][1] == p[1]:
                found = True
                freqs[i] += 1
                break
        if not found:
            pairs += [p]
            freqs += [1]
    x,y = zip(*pairs)
    area = np.pi * (dp * np.array(freqs))**2
    fig, ax = plt.subplots()
    xt = list(map(int,data["keys1"]))
    yt = list(map(int,data["keys2"]))
    ax.set_xticks(xt)
    ax.set_yticks(yt)
    ax.set_xbound(lower=xt[0]-0.5, upper=xt[-1]+0.5)
    ax.set_ybound(lower=yt[0]-0.5, upper=yt[-1]+0.5)
    ax.set_xticklabels(data["labels1"])
    ax.set_yticklabels(data["labels2"])
    ax.autoscale(enable=False, axis="both", tight=True)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
        plt.subplots_adjust(left=0.15)
    if title:
        ax.set_title(title)
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