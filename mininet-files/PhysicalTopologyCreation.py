"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.

Running : 
sudo mn --custom PhysicalTopologyCreation.py  --topo PhyTopo --controller=remote,ip=192.168.0.103 --link=tc

Host IP : 
setIP()
"""

from mininet.topo import Topo
from mininet.link import TCLink

class PhyTopo( Topo ):
	"Create Physical Topology based on specifications."

	def __init__( self ):
		"Create physical topo."

		# Initialize topology
		Topo.__init__( self )


		#Add switches
		f1 = open("phy-switches", 'r')
		switch_desc = f1.readlines()
		switchMap = dict()

		for line in switch_desc:
			lineArr = line.split()        
			switchMap[lineArr[0]] = self.addSwitch(lineArr[0])


		# Add hosts
		f2 = open("phy-hosts", 'r')
		host_desc = f2.readlines()
		hostMap = dict()

		for line in host_desc:
			lineArr = line.split()    
			hostMap[lineArr[0]] = self.addHost( lineArr[0], ip=lineArr[2], prefixLen=24)
			self.addLink( switchMap[lineArr[3]], hostMap[lineArr[0]], bw=10) 


		#Create the links between switches.
		f3 = open("phy-links", 'r')
		link_desc = f3.readlines()


		#Add Links.
		for line in link_desc:
			lineArr = line.split()
			self.addLink( switchMap[lineArr[0]],  switchMap[lineArr[1]], bw= int(lineArr[2])) 
	


topos = { 'PhyTopo': ( lambda: PhyTopo() ) }
