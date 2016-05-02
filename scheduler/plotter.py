#!/usr/bin/python
from matplotlib import pyplot as plt
import numpy as np
import glob

data = {}
flows = set() 
ratios = set()
fnames = glob.glob("F_*_R_*")
for fname in fnames:
    # Get flow param from fname
    flow_start = fname.find("F_") + 2
    flow_end = fname.find("_R_")
    flow = int(fname[flow_start:flow_end])
    flows.add(flow)

    # Get ratio param from fname
    ratio_start = flow_end + 3
    ratio = float(fname[ratio_start:])
    ratios.add(ratio)
    
    # Open file to get data
    no_sched = []
    sched = []
    with open(fname, 'r') as f:
        for line in f:
            ln = line.strip().split(",")
            no_sched.append(float(ln[0]))
            sched.append(float(ln[1]))
    data[(flow, ratio)] = (no_sched, sched)

# First make plots with number of flows fixed, ratio on x axis
for flow in sorted(flows):
    x = []
    y1 = []
    y2 = []
    for ratio in sorted(ratios):
        x.append(ratio)
        no_sched, sched = data[(flow, ratio)]
        # Average for now is prolly fine!
        y1.append(sum(no_sched)/len(no_sched))
        y2.append(sum(sched)/len(sched))
    plt.plot(x, y1)
    plt.plot(x, y2)
plt.show()
