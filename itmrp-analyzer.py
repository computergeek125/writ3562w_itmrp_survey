import argparse
import importlib
import json
import matplotlib
from matplotlib import rcParams as mp_rc
import sys

import nars as Nars
import pdplot as p
import qualtrics_api.Qv3 as Qv3
import qualtrics_api.Qv3_helpers as QH
import run_graphs
import settings
import util as u

parser = argparse.ArgumentParser()
parser.add_argument("-R", "--results", help="Sets the results file without re-downloading the results from Qualtrics", default=None)
args = parser.parse_args()

try:
    __IPYTHON__
    sys.stderr.write("Type '%matplotlib' (without the quotes) to initialize IPython\n")
except NameError:
    sys.stderr.write("Warning: This script was designed for IPython.  Running without IPython may yield unexpected results.\n")


def qualtrics_init(reuse=False):
    global q
    global args
    global survey
    global survey_data
    global N
    q = Qv3.Qualtrics_v3(settings.qualtrics_datacenter,settings.qualtrics_api_key)
    sys.stdout.write("Loading survey from Qualtrics...")

    sys.stdout.write("done!\n")
    if args.results:
        reuse = True
    else:
        survey_file = q.response_export(settings.qualtrics_survey,"json")
        sys.stdout.write("Opening {0}\n".format(survey_file))
    if reuse:
        survey_file = args.results
        sys.stdout.write("Reusing results from {0}\n".format(survey_file))
    with open(survey_file) as data_file:    
        survey_data = json.load(data_file)

    N = len(survey_data['responses'])

    survey = q.survey_get(settings.qualtrics_survey)
    sys.stdout.write("Imported {0} responses\n".format(N))

    sys.stdout.write("Survey Name: {0}\n".format(survey['name']))

def local_init():
    global nars
    global qh
    matplotlib.style.use('ggplot')
    mp_rc.update({'figure.autolayout': True})
    u.reload_window()
    nars = Nars.Nars(survey, survey_data)
    qh = QH.QHelpers(q, survey_data)

def init(reuse=False, noQ=False):
    if not noQ:
        qualtrics_init(reuse=reuse)
    local_init()

def nars_calc():
    return nars.nars(settings.nars_s1), nars.nars(settings.nars_s2), nars.nars(settings.nars_s3, inverted=True)
def nars_mrp_calc():
    return nars.nars(settings.nars_mrp_s1), nars.nars(settings.nars_mrp_s2), nars.nars(settings.nars_mrp_s3, inverted=True)

#TODO: Text analysis (report) Grab text with selectable metadata, filtering null answers

def rg(graph=None):
    run_graphs.run_graphs(graph=graph, qh=qh, nars=nars, nars_calc=nars_calc, nars_mrp_calc=nars_mrp_calc)

def reload(noQ=False):
    sys.stdout.write("Reloading local files with importlib...\n")
    importlib.reload(Nars)
    importlib.reload(p)
    importlib.reload(Qv3)
    importlib.reload(QH)
    importlib.reload(run_graphs)
    importlib.reload(settings)
    importlib.reload(u)
    init(reuse=True, noQ=noQ)

init()