#!/usr/bin/python
import argparse
import subprocess
import threading

"""
Example way to run:
python cleaner.py -u <your cs username>
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

parser.add_argument('-u', help="your cs login")
args = parser.parse_args()
user = args.u

# Run pkill on all hosts
threads = []
for host in hosts:
    cmd = ["ssh", host, "pkill", "-u", user]
    thread = threading.Thread(target=subprocess.Popen, args=[cmd])
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()
