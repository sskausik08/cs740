from FlowCharacteristic import FlowCharacteristic
from Topology import Topology
import heapq
from collections import defaultdict
import copy

T_MIN = 1 # Granularity of time to be concerned about.
T_SCHEDULER_EPOCH = 20

class FlowDatabase(object):
	def __init__(self, topo, queueSize, bandwidth=1000) :
		""" Database to store the set of flows in the network """
		self.flows = dict()
		self.flowCharacteristics = dict()
		self.paths = dict()
		self.flowID = 0
		self.topology = topo
		self.switchBytes = dict()
		self.pathCharacteristics = dict()
		self.queueSize = queueSize
		self.bandwidth = bandwidth

		self.criticalTimes = defaultdict(lambda:defaultdict(lambda:None))

		self.visited = dict()
		for sw in range(1, self.topology.getSwitchCount() + 1) :
			self.visited[sw] = False



	def addFlow(self, header, src, dst, fc) :
		self.flows[self.flowID] = [src, dst, header]
		self.flowCharacteristics[self.flowID] = fc
		
		self.pathCharacteristics[self.flowID] = dict()
		self.pathCharacteristics[self.flowID][src] = fc
		
		self.paths[self.flowID] = []
		
		self.flowID += 1
		return self.flowID - 1


	def getPath(self, flowID) : 
		if flowID in self.paths : 
			return self.paths[flowID]
		else :
			raise LookupError("No path entry for FlowID " + str(flowID))

	def changePath(self, flowID, path) : 
		prevpath = self.paths[flowID]
		self.paths[flowID] = path

		print prevpath, path
		# Update old switches on path and new switches
		for i in range(0, len(prevpath) - 1) : 
			sw1 = prevpath[i]
			sw2 = prevpath[i + 1]
			# Decrement sw1's queue to sw2 
			self.updateCriticalTime(sw1, sw2)

		print "Updated older path"

		for i in range(0, len(path) - 1) :
			sw1 = path[i]
			sw2 = path[i + 1]
			# increment sw1's queue to sw2
			self.updateCriticalTime(sw1, sw2)
			
			# Update Flow Characteristics of this flow for next switch
			if sw1 not in self.pathCharacteristics[flowID] :
				print "Characteristic does not exist!!"
				print sw1, flowID
			else : 
				# Updated fc
				fc = self.pathCharacteristics[flowID][sw1]
				TOn = fc.AvgTOn 
				rate = float(fc.AvgThroughput / TOn)
				
				totBytes = self.getTotalBytes(sw1, sw2, TOn)
				if totBytes == 0 : 
					print fc.AvgThroughput, TOn, rate
					print "Total Bytes shouldnt be zero!"
					exit(0)
				newrate = min(rate, float(self.bandwidth * float(fc.AvgThroughput/totBytes)))
				newTOn = fc.AvgThroughput / newrate
				newTOff = fc.AvgTOff - (newTOn - TOn)

				self.pathCharacteristics[flowID][sw2] = FlowCharacteristic(fc.AvgThroughput, newTOn, newTOff)
				print "Updated Characteristic at ", sw1, sw2, fc.AvgThroughput, newTOn, newTOff

			# Need to modify other flows affected by this, check if difference crosses
			# a threshold value, if yes, update the flows all the way to destination

	def getSwitchFlows(self, sw1, sw2) : 
		switchFlows = []
		for f in self.flows : 
			path = self.paths[f]
			if sw1 in path : 
				index = path.index(sw1) 
				if index < len(path) - 1 : 
					if path[index + 1] == sw2 : 
						switchFlows.append(f)

		return switchFlows
	
	def getTotalBytes(self, sw1, sw2, t) :
		switchFlows = self.getSwitchFlows(sw1, sw2)
		totBytes = 0
		for f in switchFlows : 
			fc = self.pathCharacteristics[f][sw1]
			totBytes += fc.getBytes(t)

		return totBytes

	def addSwitchBytes(self, swID, swBytes) :
		self.switchBytes[swID] = swBytes

	def updateCriticalTime(self, sw1, sw2) : 
		""" Updates the critical time for queue at sw1 going to link sw2 """
		switchFlows = self.getSwitchFlows(sw1, sw2)
		# For switchFlows, find critical time. Assuming queue size to be 0.
		t = 0
		totBytes = 0
		while totBytes < self.queueSize and t < 2 * T_SCHEDULER_EPOCH: # Dont care about event if T > 2 * epoch 
			t = t + T_MIN
			totBytes = 0
			for f in switchFlows : 
				if sw1 not in self.pathCharacteristics[f] :
					print "Characteristic does not exist!!"
					print sw1, sw2, f
				else : 
					fc = self.pathCharacteristics[f][sw1]
					totBytes += fc.getBytes(t)

		# Critical time is t 
		print "Critical time is for ",sw1, sw2, "is ", t
		self.criticalTimes[sw1][sw2] = t

	def computeCriticalEvent(self, sw1, sw2, fcNew) : 
		""" Compute updated critical event if fcNew is also placed on this path """
		switchFlows = self.getSwitchFlows(sw1, sw2)

		t = self.criticalTimes[sw1][sw2]
		print t
		totBytes = self.queueSize + 100 # Initial val
		while totBytes > self.queueSize and t > 0: 
			t = t - T_MIN
			totBytes = fcNew.getBytes(t)
			for f in switchFlows : 
				if sw1 not in self.pathCharacteristics[f] :
					print "Characteristic does not exist!!"
					print sw1, sw2, f
				else : 
					fc = self.pathCharacteristics[f][sw1]
					totBytes += fc.getBytes(t)

		print sw1, sw2, t
		t = t + T_MIN
		# Critical time is t 
		print "Computed Critical time is for ",sw1, sw2, "is ", t
		return t

	def updateCriticalTimes(self) : 
		swCount = self.topology.getSwitchCount()

		for sw in range(1, swCount + 1) : 
			neighbours = self.topology.getSwitchNeighbours(sw)
			for n in neighbours : 
				self.updateCriticalTime(sw, n)

	def findNewPath(self, fid) : 
		""" Perform a greedy depth first search for finding new path for fid """
		print "Find new path for ", fid
		src = self.getSourceSwitch(fid)
		dst = self.getDestinationSwitch(fid)

		for sw in range(1, self.topology.getSwitchCount() + 1) :
			self.visited[sw] = False

		path = self.greedyDFS(src, self.pathCharacteristics[fid][src], dst)
		return path

	def greedyDFS(self, sw, fc, dst) :
		""" At switch sw with flow characteristics fc, find a greedy path to dst"""

		if self.visited[sw] :
			# Already visited 
			return None
		else: 
			self.visited[sw] = True

		neighbours = self.topology.getSwitchNeighbours(sw)
		swPairList = []
		for n in neighbours : 
			ct = self.computeCriticalEvent(sw, n, fc) 
			# Computes critical event time if flow of fc is sent from sw to n
			# Check with cThres, should not even consider events in the same epoch
			if ct > T_SCHEDULER_EPOCH : 
				swPairList.append([n, ct])

		swPairList = sorted(swPairList, key=lambda pair: pair[1], reverse=True) # Sort by critical times
		# Greedy path search, explore switch with greatest critical time
			
		for pair in swPairList :
			nextsw = pair[0]
			if nextsw == dst : 
				# Found a path to destination
				return [sw, dst]

			updatedfc = self.findCharacteristic(sw, nextsw, fc)
			path = self.greedyDFS(nextsw, updatedfc, dst) 
			if path <> None : 
				path.insert(0, sw)
				return path
		

		# if none of the neighbours have permissible values, return None
		return None


	def findCharacteristic(self, sw1, sw2, fc) : 
		""" Find updated characteristic of fc if sent via sw1 -> sw2 """
		TOn = fc.AvgTOn 
		rate = float(fc.AvgThroughput / TOn)
		
		totBytes = self.getTotalBytes(sw1, sw2, TOn) + fc.AvgThroughput
		if totBytes == 0 : 
			print fc.AvgThroughput, TOn, rate
			print "Total Bytes shouldnt be zero!"
			exit(0)
		newrate = min(rate, float(self.bandwidth * float(fc.AvgThroughput/totBytes)))
		newTOn = fc.AvgThroughput / newrate
		newTOff = fc.AvgTOff - (newTOn - TOn)

		return FlowCharacteristic(fc.AvgThroughput, newTOn, newTOff) 


	def getSourceSwitch(self, fid) :
		return self.flows[fid][0]

	def getDestinationSwitch(self, fid) : 
		return self.flows[fid][1]

	def getSourceIP(self, fid) :
		return self.flows[fid][2][0]

	def getDestinationIP(self, fid) : 
		return self.flows[fid][2][1]

	def getCriticalSwitches(self) :
		swCount = self.topology.getSwitchCount()

		criticalSwitches = []
		for sw in range(1, swCount) : 
			neighbours = self.topology.getSwitchNeighbours(sw)
			for n in neighbours : 
				ct = self.criticalTimes[sw][n]

				if ct <= T_SCHEDULER_EPOCH : 
					# Critical time in this epoch
					criticalSwitches.append([sw,n])

		return criticalSwitches 

	def scheduleEpoch(self) : 
		self.topology.printSwitchMappings()
		# Get Critical Switches in this epoch
		criticalSwitches = self.getCriticalSwitches()

		rerouteFlows = []
		rerouteDecisions = []
		if len(criticalSwitches) == 0 : 
			return [] # No switches in critical state this epoch

		print "Critical Switches:", criticalSwitches
		for cpair in criticalSwitches : 
			sw1 = cpair[0]
			sw2 = cpair[1]
			ct = self.criticalTimes[sw1][sw2]

			switchFlows = self.getSwitchFlows(sw1, sw2)

			flowOrder = []
			for f in switchFlows : 
				if f in rerouteFlows : continue # Rerouted Flow already
				flowOrder.append([f, self.pathCharacteristics[f][sw1].getBytes(ct)])

			if len(flowOrder) == 1 :
				# One only potential flow on switch, dont reroute
				continue

			# Reroute largest flow in the switch
			flowOrder = sorted(flowOrder, key=lambda pair: pair[1], reverse=True) 

			rerouteFlowCount = 0
			for fpair in flowOrder : 
				if len(flowOrder) - rerouteFlowCount == 1 :
					# Only one flow left, dont reroute.
					break 

				f = fpair[0]
				path = self.findNewPath(f)
				if path == None :
					continue
				print "Rerouting flow ", f, " to new path ", path
				prevpath = copy.deepcopy(self.paths[f])
				self.changePath(f, path)
				rerouteFlowCount += 1
				rerouteFlows.append(f)
				rerouteDecisions.append([f, prevpath, path])

				if self.criticalTimes[sw1][sw2] > T_SCHEDULER_EPOCH : 
					# Flows have been rerouted to ensure buildup occurs after T_SCHEDULER EPOCH
					break 

		# Scheduling done. Now update all characteristics for more accurate predictions
		swCount = self.topology.getSwitchCount()
		for sw in range(1, swCount + 1) : 
			neighbours = self.topology.getSwitchNeighbours(sw)
			for n in neighbours : 
				self.updateCharacteristics(sw, n)

		return rerouteDecisions

	def updateCharacteristics(self, sw1, sw2) : 
		""" Update flow characteristics of flows going from sw1 to sw2"""
		switchFlows = self.getSwitchFlows(sw1, sw2)

		for f in switchFlows :
			fc = self.pathCharacteristics[f][sw1]
			TOn = fc.AvgTOn 
			rate = float(fc.AvgThroughput / TOn)
			
			totBytes = self.getTotalBytes(sw1, sw2, TOn)
			if totBytes == 0 : 
				print fc.AvgThroughput, TOn, rate
				print "Total Bytes shouldnt be zero!"
				exit(0)
			newrate = min(rate, float(self.bandwidth * float(fc.AvgThroughput/totBytes)))
			newTOn = fc.AvgThroughput / newrate
			newTOff = fc.AvgTOff - (newTOn - TOn)

			self.pathCharacteristics[f][sw2] = FlowCharacteristic(fc.AvgThroughput, newTOn, newTOff)























