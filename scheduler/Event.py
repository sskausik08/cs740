class Event(object):
	def __init__(self, sw1, sw2, cTime, flows) :
		""" Create a event at critical time cTime for sw1 queue to sw2 with set of flows """
		self.sw = sw1
		self.cTime = cTime
		self.nextsw = sw2
		self.flows = flows

	def getSwitch(self) : 
		return self.sw

	def getNextSwitch(self) : 
		return self.nextsw

	def getCriticalTime(self) :
		return self.cTime 

	def getFlows(self) :
		return self.flows

	def removeFlow(self, flowIDs) :
		""" Remove a list of flowIDs """
		newFlows = []
		for f in self.flows : 
			if f not in flowIDs : 
				newFlows.append(f)
		self.flows = newFlows

	def updateCriticalTime(self, fdb) :
		for f in self.flows : 
			fc = self.fdb.getFlowCharacteristic(f, self.sw, self.nextsw)
			 













