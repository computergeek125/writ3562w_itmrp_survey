# this script is designed to be run via the IPython %run magic
import matplotlib.pyplot as plt

import settings

try:
    __IPYTHON__
    pass
except NameError:
    raise RuntimeError("This script is for IPython magics")

def run_graphs(graph=None, p=None, mc2list=None, ma2list=None, mcmatrix=None, list_grouper=None, nars=None, nars_calc=None, nars_mrp_calc=None, hasqs_in_val=None):
    #demographics
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
        d = list_grouper(mc2list("Q3.5", percent=True), mc2list("Q3.8", percent=True), mc2list("Q3.11", percent=True), 
            mc2list("Q3.14", percent=True), mc2list("Q3.17", percent=True), mc2list("Q3.20", percent=True), 
            mc2list("Q3.23", percent=True), mc2list("Q3.26", percent=True))
        d = d.drop("Not applicable",0)
        f7,a7 = plt.subplots()
        f7.set_size_inches(10, 6, forward=True)
        legend = ("In Person", "Phone", "Email", "SMS", "Live Chat", "Forums", "Remote Access", "Other", "Total")
        p.pdplot(d, legend=legend, title="Tech Support Experiences", ax=a7)
    if graph is None or graph=="itsen":
        print("Plotting tech support experience (normalized)")
        d = list_grouper(mc2list("Q3.5", percent=True), mc2list("Q3.8", percent=True), mc2list("Q3.11", percent=True), 
            mc2list("Q3.14", percent=True), mc2list("Q3.17", percent=True), mc2list("Q3.20", percent=True), 
            mc2list("Q3.23", percent=True), mc2list("Q3.26", percent=True))
        d = d.drop("Not applicable",0)
        f8,a8 = plt.subplots()
        f8.set_size_inches(10, 6, forward=True)
        legend = ("In Person", "Phone", "Email", "SMS", "Live Chat", "Forums", "Remote Access", "Other", "Total")
        p.pdplot(d, legend=legend, title="Tech Support Experiences (normalized)", ax=a8)
    if graph is None or graph=="mrpe":
        print("Plotting MRP exp")
        d = mcmatrix("Q4.2")
        d = d.transpose()
        f9,a9 = plt.subplots()
        p.pdplot(d, title="MRP Experience", ax=a9, stacked=True)

    #nars
    if graph is None or graph=="nars_avg":
        print("Plotting NARS averages")
        f10,a10 = plt.subplots()
        n = nars.means(*nars_calc())
        p.pdplot(n.loc['mean'], title="MRP NARS Scores", yerr=n.loc['std'], ybound=[1,5], ax=a10)
    if graph is None or graph=="itnars_avg":
        print("Plotting IT MRP NARS averages")
        f11,a11 = plt.subplots()
        n = nars.means(*nars_mrp_calc())
        p.pdplot(n.loc['mean'], title="IT MRP NARS Scores", yerr=n.loc['std'], ybound=[1,5], ax=a11)
    
    if graph is None or graph == "nars_age":
        print("Plotting NARS split by age")
        f12,a12 = plt.subplots()
        f12.set_size_inches(9.75, 6, forward=True)
        p.nars_graphby(nars, *nars_calc(), "Q2.1", title="MRP NARS by Age Group", ybound=[1,5], ax=a12)
    if graph is None or graph == "itnars_age":
        print("Plotting IT MRP NARS split by age")
        f13,a13 = plt.subplots()
        f13.set_size_inches(9.75, 6, forward=True)
        p.nars_graphby(nars, *nars_mrp_calc(), "Q2.1", title="IT MRP NARS by Age Group", ybound=[1,5], ax=a13)
    
    if graph is None or graph == "nars_skill":
        print("Plotting NARS split by age")
        f14,a14 = plt.subplots()
        f14.set_size_inches(9.75, 6, forward=True)
        legend=("Basic", "Knowledgable", "Enthusiast", "Professional", "Other")
        p.nars_graphby(nars, *nars_calc(), "Q2.4", title="MRP NARS by Computer Skill", legend=legend, ybound=[1,5], ax=a14)
    if graph is None or graph == "itnars_skill":
        print("Plotting IT MRP NARS split by age")
        f15,a15 = plt.subplots()
        f15.set_size_inches(9.75, 6, forward=True)
        legend=("Basic", "Knowledgable", "Enthusiast", "Professional", "Other")
        p.nars_graphby(nars, *nars_mrp_calc(), "Q2.4", title="IT MRP NARS by Computer Skill", legend= legend, ybound=[1,5], ax=a15)

    if graph is None or graph == "nars_mrpe":
        print("Plotting NARS split by MRP Experience")
        f16,a16 = plt.subplots()
        hq = hasqs_in_val(["Q4.2_1", "Q4.2_2", "Q4.2_3", "Q4.2_4"], ["2", "3", "4", "5"])
        na = nars.associate_byinfo(*nars_calc(), hq)
        p.nars_graphby_info(nars, na, {True:"Has MRP experience", False:"No MRP Experience"}, title="NARS by MRP Experience", ybound=[1,5], ax=a16)
    if graph is None or graph == "itnars_mrpe":
        print("Plotting IT NARS split by MRP Experience")
        f17,a17 = plt.subplots()
        hq = hasqs_in_val(["Q4.2_1", "Q4.2_2", "Q4.2_3", "Q4.2_4"], ["2", "3", "4", "5"])
        na = nars.associate_byinfo(*nars_mrp_calc(), hq)
        p.nars_graphby_info(nars, na, {True:"Has MRP experience", False:"No MRP Experience"}, title="NARS by MRP Experience", ybound=[1,5], ax=a17)