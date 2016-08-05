import numpy as np
import pandas as pd
import sys

import settings

class QHelpers:
    def __init__(self, qualtrics_object, survey_data):
        self.q = qualtrics_object
        self.survey = self.q.survey_get(settings.qualtrics_survey)
        self.survey_data = survey_data
        self.N = len(self.survey_data['responses'])
    def mc2list(self, qcol, percent=False):
        try:
            qid = self.survey['exportColumnMap'][qcol]['question']
            question = self.survey['questions'][qid]
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
        for i in self.survey_data['responses']:
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

    def ma2list(self, qcol): #Compiles the raw respondants from a multiple-choice-multiple-answer question
        qcols = {}
        for i in self.survey['exportColumnMap'].keys():
            if i.startswith(qcol+"_"):
                if i.endswith("_TEXT"):
                    continue
                try:
                    qcols[i] = self.survey['exportColumnMap'][i]['choice'].split(".")
                except KeyError:
                    raise RuntimeError("{0} is not a multiple choice-multiple answer question\n".format(qcol))
        qn = sorted(qcols.keys(), key=lambda k: int(qcols[k][2]))
        qid = self.survey['exportColumnMap'][qn[0]]['question']
        question = self.survey['questions'][qid]
        if question['questionType']['type'] != "MC" and question['questionType']['selector'] != "MAVR":
            raise RuntimeError("{0} is not a multiple choice-multiple answer question\n".format(qcol))
            return None
        choices = question['choices']
        data = pd.Series([0]*len(qn), name=qcol, index=qn, dtype=int)
        for i in self.survey_data['responses']:
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

    def list_grouper(self, *args):
        r = pd.DataFrame([*args])
        r = r.transpose()
        return r

    def mcpaired(self, qcol1, qcol2):
        qid1 = self.survey['exportColumnMap'][qcol1]['question']
        qid2 = self.survey['exportColumnMap'][qcol2]['question']
        question1 = self.survey['questions'][qid1]
        question2 = self.survey['questions'][qid2]
        if not (question1['questionType']['type'] == "MC" and (question1['questionType']['selector'] == "SAVR" or question1['questionType']['selector'] == "SAHR")):
            sys.stderr.write("{0} is not a multiple choice, single-answer question\n".format(qcol1))
            return None
        if not (question2['questionType']['type'] == "MC" and (question2['questionType']['selector'] == "SAVR" or question2['questionType']['selector'] == "SAHR")):
            sys.stderr.write("{0} is not a multiple choice, single-answer question\n".format(qcol2))
            return None
        choices1 = question1['choices']
        choices2 = question2['choices']
        s1 = np.array([np.NaN]*self.N)
        s2 = np.array([np.NaN]*self.N)
        rids = []
        for i,j in zip(self.survey_data['responses'], range(self.N)):
            s1[j] = i[qcol1]
            s2[j] = i[qcol2]
            rids.append(i['ResponseID'])
        data = pd.DataFrame(index=rids)
        data[qcol1] = s1
        data[qcol2] = s2
        names1 = []
        keys1 = sorted(choices1.keys(), key=int)
        for i in keys1:
            names1 += [choices1[i]['choiceText']]
        names2 = []
        keys2 = sorted(choices2.keys(), key=int)
        for i in keys2:
            names2 += [choices2[i]['choiceText']]
        return {"pairs":data, "keys1":keys1,"keys2":keys2, "names1":names1,"names2":names2}

    def pairs2list(self, mcp):
        pairs = mcp['pairs']
        k1 = list(map(int, mcp['keys1']))
        k2 = list(map(int, mcp['keys2']))
        cname1 = pairs.columns[0]
        cname2 = pairs.columns[1]
        group = pairs.groupby(cname2)
        data = pd.DataFrame(index=k1)
        for i in range(len(k2)):
            k = k2[i]
            subset = group.get_group(k)[cname1]
            sums = pd.Series([0]*len(k1), index=k1)
            for i in range(len(k1)):
                ik = k1[i]
                bools = subset == ik
                sums[ik] = bools.sum()
            data[k] = sums
        data.index = mcp['names1']
        data.columns = mcp['names2']
        return data

    def mcmatrix(self, qcol):
        qcols = {}
        for i in self.survey['exportColumnMap'].keys():
            if i.startswith(qcol+"_"):
                if i.endswith("_TEXT"):
                    continue
                try:
                    qcols[i] = self.survey['exportColumnMap'][i]['subQuestion'].split(".")
                except KeyError:
                    raise RuntimeError("{0} is not a multiple choice matrix question\n".format(qcol))
        qn = sorted(qcols.keys(), key=lambda k: int(qcols[k][2]))
        qid = self.survey['exportColumnMap'][qn[0]]['question']
        question = self.survey['questions'][qid]
        if question['questionType']['type'] != "Matrix" and question['questionType']['subSelector'] != "SingleAnswer":
            raise RuntimeError("{0} is not a multiple choice matrix question\n".format(qcol))
            return None
        choices = question['choices']
        sub_questions = question['subQuestions']
        data = pd.DataFrame({})# index=range(len(choices)))
        for i in qn:
            row = self.mc2list(i)
            data[i] = row
        qnames = []
        qkeys = sorted(sub_questions.keys(), key=int)
        for i in qkeys:
            qnames += [sub_questions[i]['description']]
        data.columns = qnames
        data = data.transpose()
        return data

    def hasq_in_val(self, qcol, values):
        rids = []
        data = pd.Series(np.array([0]*self.N, dtype=np.bool))
        for i,j in zip(self.survey_data['responses'], range(self.N)):
            if i[qcol] in values:
                data[j] = True
            else:
                data[j] = False
            rids.append(i['ResponseID'])
        data.index = rids
        return data
    def hasqs_in_val(self, qcols, values):
        acc = False
        for i in qcols:
            hq = self.hasq_in_val(i, values)
            acc |= hq
        return acc