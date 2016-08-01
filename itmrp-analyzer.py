import argparse
import json
import matplotlib
from matplotlib import rcParams as mp_rc
import numpy as np
import pandas as pd
import sys
import textwrap

from qualtrics_api.Qv3 import Qualtrics_v3 as Q
import nars as Nars
#import oldplotting as op
import pdplot as p
import settings
import util as u

import run_graphs

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

sys.stderr.write("\n")
try:
    __IPYTHON__
    sys.stderr.write("Type '%matplotlib' (without the quotes) to initialize IPython\n")
except NameError:
    sys.stderr.write("Warning: This script was designed for IPython.  Running without IPython may yield unexpected results.\n")

matplotlib.style.use('ggplot')
mp_rc.update({'figure.autolayout': True})
u.reload_window()
nars = Nars.Nars(survey, survey_data)

def mc2list(qcol, percent=False):
    try:
        qid = survey['exportColumnMap'][qcol]['question']
        question = survey['questions'][qid]
    except KeyError:
        raise RuntimeError("{0} is not a multiple choice, single-answer question\n".format(qcol))
    if question['questionType']['type'] == "MC" and (question['questionType']['selector'] == "SAVR" or question['questionType']['selector'] == "SAHR"):
        matrix=False
    elif question['questionType']['type'] == "Matrix" and question['questionType']['subSelector'] == "SingleAnswer":
        matrix=True
    else:
        raise RuntimeError("{0} is not a multiple choice, single-answer type question\n".format(qcol))
        return None
    n=0
    choices = question['choices']
    ck = sorted(choices.keys(), key=int)
    data = pd.Series([0]*len(ck), name=qcol, index=ck, dtype=int)
    for i in survey_data['responses']:
        ans = i[qcol]
        if ans == "":
            pass # Throw out questions they didn't answer
        else:
            n+=1
            data[ans] += 1
    if percent:
        if n > 0:
            data = data.apply(lambda x:x/n)
    names = []
    keys = data.index
    for i in keys:
        if not matrix:
            names.append(choices[i]['choiceText'])
        else:
            names.append(choices[i]['description'])
    data.index = names
    return data

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
    data = pd.Series([0]*len(qn), name=qcol, index=qn, dtype=int)
    for i in survey_data['responses']:
        for j in i:
            if j in qn:
                ans = i[j]
                if (ans):
                    data[j] += 1
    names = []
    for i in qn:
        c = qcols[i][2]
        names.append(choices[c]['choiceText'])
    data.index = names
    return data

def list_grouper(*args):
    r = pd.DataFrame([*args])
    r = r.transpose()
    return r

def mcpaired(qcol1, qcol2):
    qid1 = survey['exportColumnMap'][qcol1]['question']
    qid2 = survey['exportColumnMap'][qcol2]['question']
    question1 = survey['questions'][qid1]
    question2 = survey['questions'][qid2]
    if question['questionType']['type'] == "MC" and (question['questionType']['selector'] == "SAVR" or question['questionType']['selector'] == "SAHR"):
        sys.stderr.write("{0} is not a multiple choice, single-answer question\n".format(qcol1))
        return None
    if question['questionType']['type'] == "MC" and (question['questionType']['selector'] == "SAVR" or question['questionType']['selector'] == "SAHR"):
        sys.stderr.write("{0} is not a multiple choice, single-answer question\n".format(qcol2))
        return None
    choices1 = question1['choices']
    choices2 = question2['choices']
    data = pd.DataFrame({qcol1:[None]*N, qcol2:[None]*N})
    for i,j in zip(survey_data['responses'], range(N)):
        data[qcol1][j] = i[qcol1]
        data[qcol2][j] = i[qcol2]
    names1 = []
    keys1 = sorted(choices1.keys(), key=int)
    for i in keys1:
        names1 += [choices1[i]['choiceText']]
    names2 = []
    keys2 = sorted(choices2.keys(), key=int)
    for i in keys2:
        names2 += [choices2[i]['choiceText']]
    return {"pairs":data, "keys1":keys1,"keys2":keys2, "names1":names1,"names2":names2}

def mcmatrix(qcol):
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
    data = pd.DataFrame({})# index=range(len(choices)))
    for i in qn:
        row = mc2list(i)
        data[i] = row
    qnames = []
    qkeys = sorted(sub_questions.keys(), key=int)
    for i in qkeys:
        qnames += [sub_questions[i]['description']]
    data.columns = qnames
    return data

def hasq_in_val(qcol, values):
    rids = []
    data = pd.Series(np.array([0]*N, dtype=np.bool))
    for i,j in zip(survey_data['responses'], range(N)):
        if i[qcol] in values:
            data[j] = True
        else:
            data[j] = False
        rids.append(i['ResponseID'])
    data.index = rids
    return data
def hasqs_in_val(qcols, values):
    acc = False
    for i in qcols:
        hq = hasq_in_val(i, values)
        acc |= hq
    return acc

def nars_calc():
    return nars.nars(settings.nars_s1), nars.nars(settings.nars_s2), nars.nars(settings.nars_s3, inverted=True)
def nars_mrp_calc():
    return nars.nars(settings.nars_mrp_s1), nars.nars(settings.nars_mrp_s2), nars.nars(settings.nars_mrp_s3, inverted=True)

#TODO: Text analysis (report) Grab text with selectable metadata, filtering null answers

def rg(graph=None):
    run_graphs.run_graphs(graph=graph, p=p, mc2list=mc2list, ma2list=ma2list, mcmatrix=mcmatrix, list_grouper=list_grouper, nars=nars, nars_calc=nars_calc, nars_mrp_calc=nars_mrp_calc, hasqs_in_val=hasqs_in_val)