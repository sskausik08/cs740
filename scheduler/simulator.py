from FlowDatabase import FlowDatabase
from FlowCharacteristic import FlowCharacteristic
from Topology import Topology
import argparse
import random


QUEUE_SIZE = 400
class Simulator(object) :
	def __init__(self, topo) : 
		self.topology = topo
		self.fdb = FlowDatabase(self.topology, QUEUE_SIZE)
		self.flows = dict()

	def addFlow(self, src, dst, fc, mice) :
		fid = self.fdb.addFlow([], src, dst, fc)
		if mice :
			self.flows[fid] = True # Mice flow
		else :
			self.flows[fid] = False # Elephant flow

		path = self.topology.getPath(src, dst)
		self.fdb.changePath(fid, path)

	def schedule(self) :
		self.fdb.updateCriticalTimes()

		reroutes = self.fdb.scheduleEpoch()
		print "Number of reroutes", len(reroutes)
		return self.computeCriticalFlowCount()

	def computeCriticalFlowCount(self) :
		swCount = self.topology.getSwitchCount()
		criticalFlows = dict()

		for f in self.flows :
			criticalFlows[f] = False

		for sw1 in range(1, swCount + 1) :
			neighbours = self.topology.getSwitchNeighbours(sw1)
			flowCaps = dict()
			# Decide input characteristics
			for sw0 in neighbours : 
				flows = self.fdb.getSwitchFlows(sw0, sw1)

				totalCap = 0
				for f in flows : 
					if self.flows[f] : 
						totalCap += 1
					else : 
						totalCap += 10

				if totalCap > 100 : 
					scalingFactor = 100/totalCap
				else :
					scalingFactor = 1

				for f in flows :
					if self.flows[f] :
						flowCaps[f] = 1 * scalingFactor
					else :
						flowCaps[f] = 10 * scalingFactor

			for sw2 in neighbours : 
				flows = self.fdb.getSwitchFlows(sw1, sw2)
				totalCap = 0
				for f in flows : 
					if f in flowCaps : 
						totalCap += flowCaps[f]
					else :
						if self.flows[f] : 
							totalCap += 1
						else : 
							totalCap += 10	
				
				if totalCap > 120 : 
					# Critical switch queue! 
					for f in flows : 
						if self.flows[f] :
							criticalFlows[f] = True

		criticalCount = 0
		for f in criticalFlows : 
			if criticalFlows[f] : 
				criticalCount += 1

		return criticalCount 


		
# topo = Topology()
# topo.addSwitch("sw1", ["sw2", "sw3", "sw4", "sw5", "sw6", "sw7"])
# topo.addSwitch("sw2", ["sw3", "sw4", "sw5", "sw6", "sw7"])
# topo.addSwitch("sw3", ["sw4", "sw5", "sw6", "sw7"])
# topo.addSwitch("sw4", ["sw5", "sw6", "sw7"])
# topo.addSwitch("sw5", ["sw6", "sw7"])
# topo.addSwitch("sw6", ["sw7"])
# topo.addSwitch("sw7", ["sw7"])


# Fat Tree topo: https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Fat_tree_network.svg/2000px-Fat_tree_network.svg.png
topo = Topology()
topo.addSwitch("sw1", ["sw2", "sw3"])
topo.addSwitch("sw2", ["sw4", "sw5"])
topo.addSwitch("sw3", ["sw6", "sw7"])
topo.addSwitch("sw4", ["sw8", "sw9"])
topo.addSwitch("sw5", ["sw10", "sw11"])
topo.addSwitch("sw6", ["sw12", "sw13"])
topo.addSwitch("sw7", ["sw14", "sw15"])



sim = Simulator(topo)
#totalFlows = 2500    Now done as commandline arguments!
#ratio = 0.95 # Mice/Total
parser = argparse.ArgumentParser()
parser.add_argument('--total', '-t', type=int, default=2500)
parser.add_argument('--ratio', '-r', type=float, default=.95)
args = parser.parse_args()
totalFlows = args.total
ratio = args.ratio

miceFlows = int(totalFlows * ratio)
elephantFlows = totalFlows - miceFlows
swCount = topo.getSwitchCount()

for i in range(miceFlows) :
	fc = FlowCharacteristic(20, 20, 2000)
	endpoints = random.sample(xrange(1, swCount+1), 2)
	sim.addFlow(endpoints[0], endpoints[1], fc, True)

for i in range(elephantFlows) :
	fc = fc = FlowCharacteristic(220, 20, 2000)
	endpoints = random.sample(xrange(1, swCount+1), 2)
	sim.addFlow(endpoints[0], endpoints[1], fc, False)

s1 = sim.computeCriticalFlowCount()
s2 = sim.schedule()
print s1, s2
