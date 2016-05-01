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
            # Hack to get around differing port pair positions
            for i, word in enumerate(ln):
                if word == '>':
                    break
            # Okay, this is a really bad hack... damn formatting inconsistencies
            if i + 1 == len(ln):
                for i, word in enumerate(ln):
                    if word == 'Source':
                        break
                srcprt = ln[i + 2]
                for i, word in enumerate(ln):
                    if word == 'Destination':
                        break
                dstprt = ln[i + 2]
            else:
                srcprt = ln[i - 1]
                dstprt = ln[i + 1]

            # Okay, I hope that covers all the bad nasty formatting stuff!
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
