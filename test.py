import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
import sys
import textwrap

from qualtrics_api.Qv3 import Qualtrics_v3 as Q

q = Q("umn.qualtrics.com","V0kaCnBnK6J9IKUsNrshV8nO6QNhbK7XJH3je0fD")

parser = argparse.ArgumentParser()
parser.add_argument("-R", "--results", help="Sets the results file without re-downloading the results from Qualtrics", default=None)
args = parser.parse_args()

survey = q.survey_get("SV_8zSxHnxahE2h0j3")
if args.results:
    survey_file = args.results
    sys.stdout.write("Reusing results from {0}\n".format(survey_file))
else:
    survey_file = q.response_export("SV_8zSxHnxahE2h0j3","json")

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

def plot_mc(qcol, title=None, xlabel=None, ylabel=None, width=0.4, color='g'):
    data = mc2list(qcol)

    pN = len(data["bars"])
    ind = np.arange(pN)  # the x locations for the groups

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, data["bars"], width, color=color)

    # add some text for labels, title and axes ticks
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(data["labels"])

    #ax.legend((rects1[0], rects2[0]), ('Men', 'Women'))
    
    mp_autolabel(rects1, ax)
    #autolabel(rects2)

    plt.show(block=False)
    return (fig, ax)

def mp_autolabel(rects, ax):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')