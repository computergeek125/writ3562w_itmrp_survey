import argparse
import json
import matplotlib
from matplotlib import rcParams as mp_rc
import numpy as np
import pandas as pd
from pprint import pprint
import sys
import textwrap

from qualtrics_api.Qv3 import Qualtrics_v3 as Q
import oldplotting as op
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
    sys.stderr.write("Type '%pylab' (without the quotes) to initialize IPython\n")
except NameError:
    sys.stderr.write("Warning: This script was designed for IPython.  Running without IPython may yield unexpected results.\n")

matplotlib.style.use('ggplot')
mp_rc.update({'figure.autolayout': True})
u.reload_window()

def new2old(pdata): 
    # Creates old-style dictionary returns from Pandas data structures
    # Ignores keys because it's not used
    return {"bars":pdata.tolist(), "names":copy(pdata.index)}

def mc2list(qcol):
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
    choices = question['choices']
    ck = sorted(choices.keys(), key=int)
    data = pd.Series([0]*len(ck), name=qcol, index=ck, dtype=int)
    for i in survey_data['responses']:
        ans = i[qcol]
        if ans == "":
            pass # Throw out questions they didn't answer
        else:
            data[ans] += 1
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
    if question1['questionType']['type'] != "MC" and question['questionType']['selector'] != "SAVR":
        sys.stderr.write("{0} is not a multiple choice, single-answer question\n".format(qcol1))
        return None
    if question2['questionType']['type'] != "MC" and question['questionType']['selector'] != "SAVR":
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

#TODO: Text analysis (report) Grab text with selectable metadata, filtering null answers
def nars_raw(nars_list, inverted=False, inversion_base=5):
    template = {}
    for i in nars_list:
        template[i] = pd.Series([np.NaN]*N, dtype=np.float64)
    rawdata = pd.DataFrame(template)
    rids = []
    for respondant,i in zip(survey_data['responses'], range(N)):
        for sq in nars_list:
            ans = respondant[sq]
            if ans == "":
                pass # Throw out questions they didn't answer
            else:
                s = int(ans)
                if inverted:
                    rawdata[sq] = likert_invert(s, inversion_base)
                else:
                    rawdata[sq][i] = s
        rids.append(respondant['ResponseID'])
    if len(nars_list) < 1:
        rawdata = pd.DataFrame(index=rids)
    else:
        rawdata.index = rids
    return rawdata
def nars(nars_list, inverted=False, inversion_base=5):
    rawdata = nars_raw(nars_list, inverted=inverted, inversion_base=inversion_base)
    nars_score = pd.DataFrame({'mean':rawdata.mean(1), 'std':rawdata.std(1)})
    return nars_score

def nars_associate(nars_s1, nars_s2, nars_s3, questions):
    resp = nars_s1.index
    template = {"nars_s1_mean":nars_s1['mean'], "nars_s1_std":nars_s1['std'], 
                "nars_s2_mean":nars_s2['mean'], "nars_s2_std":nars_s2['std'], 
                "nars_s3_mean":nars_s3['mean'], "nars_s3_std":nars_s3['std']}
    for i in questions:
        template[i] = pd.Series()
    data = pd.DataFrame(template)
    for i in survey_data['responses']:
        rid = i['ResponseID']
        if rid in resp:
            for j in questions:
                data.loc[rid][j]  = i[j]
    return data

def nars_dropNaN(nars_assoc):
    newdata = nars_assoc.copy()
    newdata = newdata[np.isfinite(newdata['nars_s1_mean'])]
    newdata = newdata[np.isfinite(newdata['nars_s2_mean'])]
    newdata = newdata[np.isfinite(newdata['nars_s3_mean'])]
    return newdata

def likert_invert(input_num, scale):
    if (scale % 2 == 0):
        raise ValueError("Likert scales must be odd numbers!  You provided a scale of {0}".format(scale))
    if (input_num < 1 or input_num > scale):
        raise ValueError("Likert scale input must be between 1 and {0} inclusive".format(scale))
    return scale - input_num +1

def print_nars(nars_processed):
    for x in nars_processed.keys():
        i = nars_processed[x]
        sys.stdout.write("{0}: m={1} s={2}\n".format(i['ResponseID'], i['mean'], i['std']))

def rg(graph=None):
    run_graphs.run_graphs(graph=graph, p=p, mc2list=mc2list, ma2list=ma2list, list_grouper=list_grouper)