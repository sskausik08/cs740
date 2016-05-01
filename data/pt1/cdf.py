#!/usr/bin/python
import glob
import numpy as np
from matplotlib import pyplot as plt

for fname in glob.glob("*.*.*.*"):
    flows = {}
    with open(fname, 'r') as f:
        for line in f:
            ln = line.split()
            time = float(ln[1])
            srcip = ln[2]
            dstip = ln[4]
            srcprt = ln[7]
            dstprt = ln[9]
            key = srcip + ":" + srcprt + " -> " + dstip + ":" + dstprt
            if key not in flows.keys():
                flows[key] = [] 
            flows[key].append(time)

    for key in flows.keys():
        times = flows[key]
        # Sort just in case (shouldn't make a difference)
        times.sort()

        percents = []
        cumulative = 0
        for time in times:
            cumulative += time
            percents.append(cumulative)

        # Normalize
        for i in range(len(percents)):
            percents[i] = percents[i] / cumulative

        plt.step(times, percents)
        plt.title(key)
        plt.xlabel("Time (s)")
        plt.ylabel("% of packets (t <= T)")
        plt.show()
