# this script is designed to be run via the IPython %run magic
import matplotlib.pyplot as plt

import settings

try:
    __IPYTHON__
    pass
except NameError:
    raise RuntimeError("This script is for IPython magics")

def run_graphs(graph=None, p=None, mc2list=None, ma2list=None, list_grouper=None):
    if graph is None or graph=="age":
        print("Plotting age demographics")
        f1,a1 = plt.subplots()
        a1 = p.pdplot(mc2list("Q2.1"), title="Age")
    if graph is None or graph=="cu":
        print("Plotting computer usage")
        f2,a2 = plt.subplots()
        a2 = p.pdplot(mc2list("Q2.2"), title="Computer Use")
    if graph is None or graph=="cul":
        print("Plotting computer usage location")
        f3,a3 = plt.subplots()
        a3 = p.pdplot(ma2list("Q2.3"), title="Computer Use Location", label_clip=30)
    if graph is None or graph=="cn":
        print("Plotting computer knowledge")
        f4,a4 = plt.subplots()
        a4 = p.pdplot(mc2list("Q2.4"), title="Computer Knowledge", xtick_labels=settings.cQ2_4_short)
    if graph is None or graph=="ge":
        print("Plotting games enjoyed")
        f4,a4 = plt.subplots()
        a4 = p.pdplot(ma2list("Q2.5"), title="Games Enjoyed", xtick_labels=settings.cQ2_5_short)
    if graph is None or graph=="itss":
        print("Plotting IT support sources")
        f5,a5 = plt.subplots()
        a5 = p.pdplot(ma2list("Q3.1"), title="Sorurces of IT support", xtick_labels=settings.cQ3_1_short)
    if graph is None or graph=="itse":
        print("Plotting tech support experience")
        d = list_grouper(mc2list("Q3.5"), mc2list("Q3.8"), mc2list("Q3.11"), mc2list("Q3.14"), mc2list("Q3.17"), mc2list("Q3.20"), mc2list("Q3.23"), mc2list("Q3.26"))
        d = d.drop("Not applicable",0)
        #f6,a6 = plt.subplots()
        a6 = p.pdplot(d, legend=("In Person", "Phone", "Email", "SMS", "Live Chat", "Forums", "Remote Access", "Other"), title="Tech Support Experiences")

#f,x = plot_mc("Q2.1", listifier=mc2list, label_length=15, label_clip=30, title="Age")
#f,x = plot_mc("Q2.2", listifier=mc2list, label_length=15, label_clip=30, title="Computer Use")
#f,x = plot_mc("Q2.3", listifier=ma2list, label_length=15, label_clip=30, title="Computer Use Location")
#f,x = plot_mc("Q2.4", listifier=mc2list, label_length=15, label_clip=30, title="Computer Knowledge", xtick_rotation=-45, xtick_labels=settings.cQ2_4_short)
#f,x = plot_mc("Q2.5", listifier=ma2list, label_length=18, label_clip=30, title="Games Enjoyed", xtick_rotation=-60, xtick_labels=settings.cQ2_5_short)
#f,x = plot_mc(ma2list("Q3.1"), title="Sorurces of IT support", xtick_labels=settings.cQ3_1_short)
#f,x = plot_mc(d, legend=("In Person", "Phone", "Email", "SMS", "Live Chat", "Forums", "Remote Access", "Other"), title="Tech Support Experiences")