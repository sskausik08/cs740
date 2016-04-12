#!/usr/bin/python
import numpy as np

class Flow_Characteristic:
    # Constructor, tell it how long of a history to keep
    def __init__(self, n_elts):
        self.history = np.zeros(n_elts)
        self.curr = 0
        
    # Get the "best" value, determined by value at 50% of sum
    def get_best(self):
        s = sum(self.history)
        p = 0
        for i in np.sort(self.history):
            p += i
            if p >= .5*s:
                break
        return i

    # Insert a value into the flow's history
    def insert(self, value):
        self.history[self.curr] = value
        self.curr += 1
        self.curr %= len(self.history)
