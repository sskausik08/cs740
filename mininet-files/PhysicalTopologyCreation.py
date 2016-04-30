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
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.cli import CLI

import time


class PhyTopo( Topo ):
	"Create Physical Topology based on specifications."

	def __init__( self ):
		"Create physical topo."

		# Initialize topology
		Topo.__init__( self )


		print "Topology Instantiation"
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
			self.addLink( switchMap[lineArr[0]],  switchMap[lineArr[1]], bw= float(lineArr[2]), max_queue_size=500) 
	

#topos = { 'PhyTopo': ( lambda: PhyTopo() ) }

def perfTest():
	"Create network and run simple performance test"
	print "Here"
	scheduler = RemoteController( 'scheduler', ip='192.168.56.1', port=6633 )
	topo = PhyTopo()
	net = Mininet(topo=topo, 
				  host=CPULimitedHost, link=TCLink, build=False)
	net.addController(scheduler)
	net.build()


	# Set MAC addresses 
	f1 = open("phy-hosts", 'r')
	host_desc = f1.readlines()

	for line in host_desc:
		lineArr = line.split()
		host = net.get(lineArr[0])
		ip = lineArr[2].split(".")
		ethstr = str("00:00:00:00:00:") + ip[3]
		host.setMAC(ethstr)
		

	net.start()
	time.sleep(15)
	h1, h4 = net.get('h1', 'h4')
	net.iperf((h1, h4))
	net.pingAll()
	net.pingAll()
	


if __name__ == '__main__':
	setLogLevel('info')
	perfTest()

