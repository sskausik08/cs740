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
print a

# Only include packets with a source & dest in the sampled set
for fname in a:
    with open(fname, 'r') as inFile, open("samples/" + fname, 'w') as outFile:
        for line in inFile:
            outFile.write(line)
