# this script is designed to be run via the IPython %run magic
import matplotlib.pyplot as plt

import settings

try:
    __IPYTHON__
    pass
except NameError:
    raise RuntimeError("This script is for IPython magics")

def run_graphs(graph=None, p=None, mc2list=None, ma2list=None, list_grouper=None, nars=None):
    if graph is None or graph=="age":
        print("Plotting age demographics")
        f1,a1 = plt.subplots()
        p.pdplot(mc2list("Q2.1"), title="Age", ax=a1)
    if graph is None or graph=="cu":
        print("Plotting computer usage")
        f2,a2 = plt.subplots()
        p.pdplot(mc2list("Q2.2"), title="Computer Use", ax=a2)
    if graph is None or graph=="cul":
        print("Plotting computer usage location")
        f3,a3 = plt.subplots()
        p.pdplot(ma2list("Q2.3"), title="Computer Use Location", label_clip=30, ax=a3)
    if graph is None or graph=="cn":
        print("Plotting computer knowledge")
        f4,a4 = plt.subplots()
        p.pdplot(mc2list("Q2.4"), title="Computer Knowledge", xtick_labels=settings.cQ2_4_short, ax=a4)
    if graph is None or graph=="ge":
        print("Plotting games enjoyed")
        f5,a5 = plt.subplots()
        p.pdplot(ma2list("Q2.5"), title="Games Enjoyed", xtick_labels=settings.cQ2_5_short, ax=a5)
    if graph is None or graph=="itss":
        print("Plotting IT support sources")
        f6,a6 = plt.subplots()
        p.pdplot(ma2list("Q3.1"), title="Sorurces of IT support", xtick_labels=settings.cQ3_1_short, ax=a6)
    if graph is None or graph=="itse":
        print("Plotting tech support experience")
        d = list_grouper(mc2list("Q3.5"), mc2list("Q3.8"), mc2list("Q3.11"), mc2list("Q3.14"), mc2list("Q3.17"), mc2list("Q3.20"), mc2list("Q3.23"), mc2list("Q3.26"))
        d = d.drop("Not applicable",0)
        f7,a7 = plt.subplots()
        p.pdplot(d, legend=("In Person", "Phone", "Email", "SMS", "Live Chat", "Forums", "Remote Access", "Other"), title="Tech Support Experiences", ax=a7)
    if graph is None or graph is "nars_age":
        print("Plotting NARS split by age")
        f8,a8 = plt.subplots()
        p.nars_graphby(nars,nars.nars(settings.nars_s1), nars.nars(settings.nars_s2), nars.nars(settings.nars_s3, inverted=True), "Q2.1", title="NARS by Age Group" ax=a8)

#f,x = plot_mc("Q2.1", listifier=mc2list, label_length=15, label_clip=30, title="Age")
#f,x = plot_mc("Q2.2", listifier=mc2list, label_length=15, label_clip=30, title="Computer Use")
#f,x = plot_mc("Q2.3", listifier=ma2list, label_length=15, label_clip=30, title="Computer Use Location")
#f,x = plot_mc("Q2.4", listifier=mc2list, label_length=15, label_clip=30, title="Computer Knowledge", xtick_rotation=-45, xtick_labels=settings.cQ2_4_short)
#f,x = plot_mc("Q2.5", listifier=ma2list, label_length=18, label_clip=30, title="Games Enjoyed", xtick_rotation=-60, xtick_labels=settings.cQ2_5_short)
#f,x = plot_mc(ma2list("Q3.1"), title="Sorurces of IT support", xtick_labels=settings.cQ3_1_short)
#f,x = plot_mc(d, legend=("In Person", "Phone", "Email", "SMS", "Live Chat", "Forums", "Remote Access", "Other"), title="Tech Support Experiences")