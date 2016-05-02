import numpy as np
import argparse
import subprocess

"""
Example way to run:
python runner.py -f 500 -F 5000 -n 10 -r 0 -R 1 -m 11 -p simulator.py
"""

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

print flows, ratios
for flow in flows:
    for ratio in ratios:
        subprocess.call(["python", path, "-t", str(int(flow)), "-r",
            str(ratio), "-o", "F_" + str(int(flow)) + "_R_" + str(ratio)])
