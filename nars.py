import numpy as np
import pandas as pd

class Nars:
    def __init__(self, survey, survey_data):
        if not survey:
            raise RuntimeError("You must specify a survey!")
        if not survey_data:
            raise RuntimeError("You must specify survey data!")
        self.survey = survey
        self.survey_data = survey_data
        self.N = len(survey_data['responses'])
    def nars_raw(self, nars_list, inverted=False, inversion_base=5):
        template = {}
        for i in nars_list:
            template[i] = pd.Series([np.NaN]*self.N, dtype=np.float64)
        rawdata = pd.DataFrame(template)
        rids = []
        for respondant,i in zip(self.survey_data['responses'], range(self.N)):
            for sq in nars_list:
                ans = respondant[sq]
                if ans == "":
                    pass # Throw out questions they didn't answer
                else:
                    s = int(ans)
                    if inverted:
                        rawdata[sq][i] = self.likert_invert(s, inversion_base)
                    else:
                        rawdata[sq][i] = s
            rids.append(respondant['ResponseID'])
        if len(nars_list) < 1:
            rawdata = pd.DataFrame(index=rids)
        else:
            rawdata.index = rids
        return rawdata
    def nars(self, nars_list, inverted=False, inversion_base=5):
        rawdata = self.nars_raw(nars_list, inverted=inverted, inversion_base=inversion_base)
        nars_score = pd.DataFrame({'mean':rawdata.mean(1), 'std':rawdata.std(1)})
        return nars_score

    def mean(self, nars_s):
        nmv = nars_s['mean']
        return pd.Series([nmv.mean(), nmv.std()], index=["mean", "std"])
    def means(self, nars_s1, nars_s2, nars_s3):
        data = {"NARS S1":self.mean(nars_s1), "NARS S2":self.mean(nars_s2), "NARS S3":self.mean(nars_s3)}
        return pd.DataFrame(data)

    def associate_mc(self, nars_s1, nars_s2, nars_s3, questions):
        resp = nars_s1.index
        template = {"nars_s1_mean":nars_s1['mean'], "nars_s1_std":nars_s1['std'], 
                    "nars_s2_mean":nars_s2['mean'], "nars_s2_std":nars_s2['std'], 
                    "nars_s3_mean":nars_s3['mean'], "nars_s3_std":nars_s3['std']}
        for i in questions:
            template[i] = pd.Series()
        data = pd.DataFrame(template)
        for i in self.survey_data['responses']:
            rid = i['ResponseID']
            if rid in resp:
                for j in questions:
                    data.loc[rid][j]  = i[j]
        return data

    def associate_ma(self, nars_s1, nars_s2, nars_s3, questions):
        resp = nars_s1.index
        template = {"nars_s1_mean":nars_s1['mean'], "nars_s1_std":nars_s1['std'], 
                    "nars_s2_mean":nars_s2['mean'], "nars_s2_std":nars_s2['std'], 
                    "nars_s3_mean":nars_s3['mean'], "nars_s3_std":nars_s3['std']}
        if len(questions) > 1:
            raise NotImplementedError("Processing batches of questions is not possible at this time")
        qcols = {}
        for i in self.survey['exportColumnMap'].keys():
            if i.startswith(questions[0]+"_"):
                if i.endswith("_TEXT"):
                    continue
                try:
                    qcols[i] = self.survey['exportColumnMap'][i]['choice'].split(".")
                except KeyError:
                    raise RuntimeError("{0} is not a multiple choice-multiple answer question\n".format(qcol))
        qn = sorted(qcols.keys(), key=lambda k: int(qcols[k][2]))
        for i in qn:
            template[i] = pd.Series()
        data = pd.DataFrame(template)
        for i in self.survey_data['responses']:
            rid = i['ResponseID']
            if rid in resp:
                for j in qn:
                    if i[j]:
                        a = 1
                    else:
                        a = 0
                    data.loc[rid][j]  = a
        return data

    def dropNaN(self, nars_assoc, ignore=[]):
        newdata = nars_assoc.copy()
        if 's1' not in ignore:
            newdata = newdata[np.isfinite(newdata['nars_s1_mean'])]
        if 's2' not in ignore:
            newdata = newdata[np.isfinite(newdata['nars_s2_mean'])]
        if 's3' not in ignore:
            newdata = newdata[np.isfinite(newdata['nars_s3_mean'])]
        return newdata

    def associate_ma_mean(self, nars_assoc, qcol):
        #nars_assoc = self.dropNaN(nars_assoc)
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
        base = {}
        idx = ['nars_s1_mean', 'nars_s1_std', 'nars_s2_mean', 'nars_s2_std', 'nars_s3_mean', 'nars_s3_std']
        for i in qn:
            subset = nars_assoc.loc[nars_assoc[i] == 1]
            ns1m = subset['nars_s1_mean'].mean()
            ns1s = subset['nars_s1_mean'].std()
            ns2m = subset['nars_s2_mean'].mean()
            ns2s = subset['nars_s2_mean'].std()
            ns3m = subset['nars_s3_mean'].mean()
            ns3s = subset['nars_s3_mean'].std()
            pds = pd.Series([ns1m, ns1s, ns2m, ns2s, ns3m, ns3s], dtype=np.float64)
            base[qcols[i][2]] = pds
        data = pd.DataFrame(base, columns=sorted(base.keys(), key=int))
        data.index = idx
        columns = []
        #ecols 
        for i in range(len(data.columns)):
            columns.append(choices[data.columns[i]]['choiceText'])
        data.columns = columns
        return data

    def associate_mc_mean(self, nars_assoc, qcol):
        #nars_assoc = self.dropNaN(nars_assoc)
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
        choices = question['choices']
        base = {}
        idx = ['nars_s1_mean', 'nars_s1_std', 'nars_s2_mean', 'nars_s2_std', 'nars_s3_mean', 'nars_s3_std']
        for i in choices.keys():
            subset = nars_assoc.loc[nars_assoc[qcol] == int(i)]
            ns1m = subset['nars_s1_mean'].mean()
            ns1s = subset['nars_s1_mean'].std()
            ns2m = subset['nars_s2_mean'].mean()
            ns2s = subset['nars_s2_mean'].std()
            ns3m = subset['nars_s3_mean'].mean()
            ns3s = subset['nars_s3_mean'].std()
            pds = pd.Series([ns1m, ns1s, ns2m, ns2s, ns3m, ns3s], dtype=np.float64)
            base[i] = pds
        data = pd.DataFrame(base)
        data.index = idx
        columns = []
        #ecols 
        for i in range(len(data.columns)):
            columns.append(choices[data.columns[i]]['choiceText'])
        data.columns = columns
        return data

    def associate_byinfo(self, nars_s1, nars_s2, nars_s3, info):
        #resp = nars_s1.index
        #print(nars_s1['mean'])
        template = {"nars_s1_mean":nars_s1['mean'], "nars_s1_std":nars_s1['std'], 
                    "nars_s2_mean":nars_s2['mean'], "nars_s2_std":nars_s2['std'], 
                    "nars_s3_mean":nars_s3['mean'], "nars_s3_std":nars_s3['std']}
        data = pd.DataFrame(template)
        #print(template)
        #print(data)
        data['info'] = info
        return data

    def associate_byinfo_mean(self, nars_assoc, info_labels):
        #nars_assoc = self.dropNaN(nars_assoc)
        base = {}
        idx = ['nars_s1_mean', 'nars_s1_std', 'nars_s2_mean', 'nars_s2_std', 'nars_s3_mean', 'nars_s3_std']
        for i in info_labels.keys():
            subset = nars_assoc.loc[nars_assoc['info'] == int(i)]
            ns1m = subset['nars_s1_mean'].mean()
            ns1s = subset['nars_s1_mean'].std()
            ns2m = subset['nars_s2_mean'].mean()
            ns2s = subset['nars_s2_mean'].std()
            ns3m = subset['nars_s3_mean'].mean()
            ns3s = subset['nars_s3_mean'].std()
            pds = pd.Series([ns1m, ns1s, ns2m, ns2s, ns3m, ns3s], dtype=np.float64)
            base[i] = pds
        data = pd.DataFrame(base)
        data.index = idx
        columns = []
        #ecols 
        for i in range(len(data.columns)):
            columns.append(info_labels[data.columns[i]])
        data.columns = columns
        return data

    def likert_invert(self, input_num, scale):
        if (scale % 2 == 0):
            raise ValueError("Likert scales must be odd numbers!  You provided a scale of {0}".format(scale))
        if (input_num < 1 or input_num > scale):
            raise ValueError("Likert scale input must be between 1 and {0} inclusive".format(scale))
        return scale - input_num +1