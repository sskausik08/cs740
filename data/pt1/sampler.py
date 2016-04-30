#!/usr/bin/python
import glob
import argparse
import random
import hashlib

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
    d[host] = "10.0.0." + str(i + 1)

# Only include packets with a source & dest in the sampled set
for fname in a:
    with open(fname, 'r') as inFile, open("samples/"+d[fname], 'w') as outFile:
        for line in inFile:
            ln = line.split()

            # Perform mapping on src & dest and write
            ln[2] = d[ln[2]]

            # Want a closed set of hosts, so we hash destination ip & mod #hosts
            dsthash = hashlib.md5(b'' + ln[4])
            ln[4] = '10.0.0.' + str(1 + (int(dsthash.hexdigest(), 16) % len(a)))
            # Hack to make not send to self
            if ln[4] = ln[2]:
                ln[4] = '10.0.0.' + str(1 + ((1 + int(dsthash.hexdigest(), 16)) % len(a)))
            line = " ".join(ln)
            outFile.write(line)
