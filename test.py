import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
import sys
import textwrap

from qualtrics_api.Qv3 import Qualtrics_v3 as Q

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

with open(survey_file) as data_file:    
    survey_data = json.load(data_file)

N = len(survey_data['responses'])
print("Imported {0} responses".format(N))

def mc2list(qcol):
    qid = survey['exportColumnMap'][qcol]['question']
    question = survey['questions'][qid]
    if question['questionType']['type'] != "MC":
        sys.stderr.write("{0} is not a multiple choice question\n".format(qcol))
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
    keys = sorted(list(rdata_raw.keys()))
    for i in keys:
        bars += [rdata_raw[i]]
        names += [choices[i]['choiceText']]
    labels=[textwrap.fill(text,15) for text in names]
    return {"keys":keys, "bars":bars, "names":names, "labels":labels}

def plot_mc(qcol, title=None, xlabel=None, ylabel=None, width=0.4, color='g', alpha=0.5):
    # based on: http://matplotlib.org/examples/api/barchart_demo.html
    data = mc2list(qcol)

    pN = len(data["bars"])
    ind = np.arange(pN)  # the x locations for the groups

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, data["bars"], width, color=color)

    # add some text for labels, title and axes ticks
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(data["labels"])

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
    keys1 = sorted(list(choices1.keys()))
    for i in keys1:
        names1 += [choices1[i]['choiceText']]
    if len(names1) == len(keys1)-1:
        names1 += ['Other']
    labels1=[textwrap.fill(text,15) for text in names1]
    names2 = []
    keys2 = sorted(list(choices2.keys()))
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
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')