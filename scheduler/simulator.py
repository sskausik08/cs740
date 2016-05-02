from FlowDatabase import FlowDatabase
from FlowCharacteristic import FlowCharacteristic
from Topology import Topology

QUEUE_SIZE = 1000
class simulator(object) :
	def __init__(self, topo) : 
		self.fdb = FlowDatabase(self.topology, QUEUE_SIZE)
		self.topo = topo

	def addFlow(self) :
		pass

	def schedule() :
		self.fdb.updateCriticalTimes()

		self.fdb.scheduleEpoch()
		paths = self.fdb.getPaths()

	def computeCriticalFlowCount(self, paths) :
		return 0






