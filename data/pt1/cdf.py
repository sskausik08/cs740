#!/usr/bin/python
import glob
import numpy as np
from matplotlib import pyplot as plt

for fname in glob.glob("*.*.*.*"):
    times = []
    with open(fname, 'r') as f:
        for line in f:
            ln = line.split()
            time = float(ln[1])
            times.append(time)

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
    plt.title(fname)
    plt.xlabel("Time (s)")
    plt.ylabel("% of packets")
    plt.show()
