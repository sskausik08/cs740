from Topology import Topology
from FlowDatabase import FlowDatabase

class Scheduler(object):
	""" Scheduling flows """

	def __init__(self, topo) :
		self.topology = topo

		self.fdb = FlowDatabase()
	

	def findNewPath(self, fid) : 
		""" Perform a greedy depth first search for finding new path for fid """
		src = self.fdb.getSourceSwitch(fid)
		dst = self.fdb.getSourceSwitch(fid)

	def greedyDFS(self, sw, fc, dst, cThres) :
		""" At switch sw with flow characteristics fc, find a greedy path to dst"""
		neighbours = self.topology.getSwitchNeighbours(sw)
		swPairList = []
		for n in neighbours : 
			ct = self.fdb.computeCriticalEvent(sw, n, fc) 
			# Computes critical event time if flow of fc is sent from sw to n
			# Check with cThres, should not even consider events in the same epoch
			if ct > cThres : 
				swPairList.append([n, ct])

		swPairList = sorted(swPairList, key=lambda pair: pair[1], reverse=True) # Sort by critical times
		# Greedy path search, explore switch with greatest critical time
			
		for pair in swPairList :
			nextsw = pair[0]
			if nextsw == dst : 
				# Found a path to destination
				return [sw, dst]
			updatedfc = 0 # If  sw-nextsw link is chosen, find updated fc
			path = self.greedyDFS(nextsw, updatedfc, dst, cThres) 
			if path <> None : 
				path.insert(sw, 0)
				return path

		# if none of the neighbours have permissible values, return None
		return None











t = Topology()
t.addSwitch("a0", ["a1", "a2"])
t.addSwitch("a1", ["a2", "a3"])
t.addSwitch("a2", ["a4"])
s = Scheduler(t)