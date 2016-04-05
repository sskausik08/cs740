from Topology import Topology

class Scheduler(object):
	""" Scheduling flows """

	def __init__(self, topo) :
		self.topology = topo


t = Topology()
t.addSwitch("a0", ["a1", "a2"])
t.addSwitch("a1", ["a2", "a3"])
t.addSwitch("a2", ["a4"])
s = Scheduler(t)