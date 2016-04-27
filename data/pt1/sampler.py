#!/usr/bin/python
import glob
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('-n', type=int)
args = parser.parse_args()
fnames = glob.glob("*.*.*")

# Sample the given number of files 
t = 0
m = 0
n = args.n
N = len(fnames)
a = set() # Set we'll store the sample in
for fname in fnames:
    U = random.random()
    if U*(N-t) < n - m:
        a.add(fname)
        m += 1
    t += 1

# Set up mapping Don't sample more than 256 things!
d = {}
for i, host in enumerate(a):
    d[host] = "10.0.0." + str(i)

# Only include packets with a source & dest in the sampled set
for fname in a:
    with open(fname, 'r') as inFile, open("samples/"+d[fname], 'w') as outFile:
        for line in inFile:
            ln = line.split()
            # Want a closed set of hosts
            if ln[4] in a:
                # Perform mapping and write
                ln[2] = d[ln[2]]
                ln[4] = d[ln[4]]
                line = " ".join(ln)
                outFile.write(line)
