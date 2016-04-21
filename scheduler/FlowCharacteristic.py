#!/usr/bin/python

class FlowCharacteristic:
    # Constructor, tell it how long of a history to keep
    def __init__(self):
        self.AvgThroughput = 0
        self.AvgTOn = 0
        self.AvgTOff = 0
        self.ewmaConst = 0.2

        self.Throughput = 0
        self.TOn = 0
        self.TOff = 0

        self.prevBytes = 0
        self.prevTime = 0
        self.prevOnFlag = False
        
    # Get the "best" value, determined by value at 50% of sum
    def getBytes(self, t=100) :
        if self.AvgTOn == 0 or self.AvgTOff == 0 : 
            return 0
        periods = t/(self.AvgTOn + self.AvgTOff)
        return self.AvgThroughput * (periods) 

    # Insert a value into the flow's history
    def insert(self, byteValue, timeValue):
        byteVal = byteValue - self.prevBytes
        interval = timeValue - self.prevTime
        print byteVal, interval
        if byteVal > 0 :
            # On Time
            self.Throughput += byteVal
            self.TOn += interval

            if not self.prevOnFlag : 
                # OFF -> ON
                self.AvgTOff = (1 - self.ewmaConst) * self.AvgTOff + self.ewmaConst * self.TOff 
                self.TOff = 0
                print "average off times is", self.AvgTOff

            self.prevOnFlag = True
        else : 
            # Off time
            self.TOff += interval

            if self.prevOnFlag : 
                # ON -> OFF
                self.AvgThroughput = (1 - self.ewmaConst) * self.AvgThroughput + self.ewmaConst * self.Throughput
                self.AvgTOn = (1 - self.ewmaConst) * self.AvgTOn + self.ewmaConst * self.TOn
                self.TOn = 0
                self.Throughput = 0

            self.prevOnFlag = False

        self.prevBytes = byteValue
        self.prevTime = timeValue

        print "Stat", self.AvgThroughput, self.AvgTOn, self.AvgTOff


        
