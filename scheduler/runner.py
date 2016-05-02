#!/usr/bin/python
import numpy as np
import argparse
import subprocess
import threading

"""
Example way to run:
python runner.py -f 500 -F 5000 -n 10 -r 0 -R 1 -m 11 -p simulator.py
"""

# First build list of cs machine host names
hosts = []
for i in range(9):
    if i < 9:
        hosts.append("macaroni-0" + str(1 + i))
    else:
        hosts.append("macaroni-" + str(1 + i))

for i in range(30):
    if i < 9:
        hosts.append("galapagos-0" + str(1 + i))
    else:
        hosts.append("galapagos-" + str(1 + i))

for i in range(10):
    if i < 9:
        hosts.append("king-0" + str(1 + i))
    else:
        hosts.append("king-" + str(1 + i))

for i in range(7):
    if i < 9:
        hosts.append("adelie-0" + str(1 + i))
    else:
        hosts.append("adelie-" + str(1 + i))

parser = argparse.ArgumentParser()

parser.add_argument('-p', help="path to simulator (needed for distributing)")
parser.add_argument('-f', type=int, help="lower bound for number of flows")
parser.add_argument('-F', type=int, help="upper bound for number of flows")
parser.add_argument('-n', type=int, help="number of flow numbers to run over"
                    "(note, should result in integer step size!)")

parser.add_argument('-r', type=float, help="lower ratio bound")
parser.add_argument('-R', type=float, help="upper ratio bound")
parser.add_argument('-m', type=float, help="number of ratio numbers to run over")

args = parser.parse_args()

flows = np.linspace(args.f, args.F, args.n)
ratios = np.linspace(args.r, args.R, args.m)
path = args.p

# Run simulator for all combinations of flows and ratios, distribute among hosts
i = 0
threads = []
for flow in flows:
    for ratio in ratios:
        cmd = ["ssh", hosts[i], "python", path, "-t", str(int(flow)), "-r", str(ratio), "-o", "F_" + str(int(flow)) + "_R_" + str(ratio)]
        i = (i + 1) % len(hosts) # Advance to next host
        thread = threading.Thread(target=subprocess.Popen, args=[cmd])
        thread.start()
        threads.append(thread)

for thread in threads:
    thread.join()
