from FlowCharacteristic import FlowCharacteristic
from Topology import Topology
class FlowDatabase(object):
	def __init__(self, topo) :
		""" Database to store the set of flows in the network """
		self.flows = dict()
		self.flowCharacteristics = dict()
		self.paths = dict()
		self.flowID = 0
		self.topology = topo

	def addFlow(self, header, src, dst, fc) :
		self.flows[self.flowID] = [src, dst, header]
		self.flowCharacteristics[self.flowID] = fc
		self.flowID += 1
		return self.flowID - 1

	def addPath(self, flowID, path) :
		self.paths[flowID] = path

	def getPath(self, flowID) : 
		if flowID in self.paths : 
			return self.paths[flowID]
		else :
			raise LookupError("No path entry for FlowID " + str(flowID))

	def changePath(self, flowID, path) :
		prevpath = self.paths[flowID]
		self.paths[flowID] = path

		# Update Flow characteristics along the path now
		swReroute = 0 
		for swReroute in range(len(path) - 1) : 
			if prevpath[swReroute] <> path[swReroute] :
				break

		# Update old switches on path and new switches
		for i in range(swReroute, len(prevpath) - 1) : 
			sw1 = path[i]
			sw2 = path[i + 1]
			# Decrement sw1's queue to sw2 

		for i in range(swReroute, len(path) - 1) :
			sw1 = path[i]
			sw2 = path[i + 1]
			# increment sw1's queue to sw2

			# Update Flow Characteristics of this flow for next switch
			
			# Need to modify other flows affected by this, check if difference crosses
			# a threshold value, if yes, update the flows all the way to destination
		
					

	def updateCriticalTime(self, sw1, sw2) : 
		""" Updates the critical time for queue at sw1 going to link sw2 """
		switchFlows = []
		for f in self.flows : 
			path = self.paths[f]
			if sw1 in path : 
				index = path.index(sw1) 
				if index < len(path) - 1 : 
					if path[index + 1] == sw2 : 
						switchFlows.append(f)

		# For switchFlows, find critical time 



	def getBytes(self, flowID, t) : 
		""" Returns the predicted amount of bytes for flowID in time interval t"""
		# Stephen's Code.




