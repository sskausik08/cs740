from pox.core import core
from collections import defaultdict

import pox.forwarding.l2_learning
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
import pox.openflow.discovery
import pox.openflow.spanning_tree
import pox.proto.arp_responder
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.vlan import vlan
from pox.lib.packet.ipv4 import ipv4 
from  pox.lib.packet.arp import arp
from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr
from pox.lib.recoco import Timer
from pox.openflow.of_json import *

from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os 
import sys
import time
from Topology import Topology
from FlowCharacteristic import FlowCharacteristic
from FlowDatabase import FlowDatabase
log = core.getLogger()

hostMap = dict()
hostMap["10.0.0.1"] = "s1"
hostMap["10.0.0.2"] = "s4"

macMap = dict()
macMap["10.0.0.1"] = EthAddr("00:00:00:00:00:01")
macMap["10.0.0.2"] = EthAddr("00:00:00:00:00:02")

EthAddr("00:00:00:00:00:01")

QUEUE_SIZE = 500 # In Kbytes

class Scheduler (EventMixin):

	def __init__(self):
		self.listenTo(core.openflow)
		core.openflow_discovery.addListeners(self)
		log.debug("Enabling NetworkMapper Module")

		# Adjacency map.  [sw1][sw2] -> port from sw1 to sw2
		self.adjacency = defaultdict(lambda:defaultdict(lambda:None))
		
		self.switchMap = dict()
		self.switchConnections = dict()

		self.topology = Topology()

		self.fdb = FlowDatabase(self.topology)

		self.routeStatus = []

		self.startTime = time.time()

		self.measurementEpoch = 5 
		self.measurementInfra = Timer(self.measurementEpoch, self._measurement, recurring=True)

		self.schedulerEpoch = 100
		self.scheduler = Timer(self.schedulerEpoch, self._scheduler, recurring=True)

		
	"""This event will be raised each time a switch will connect to the controller"""
	def _handle_ConnectionUp(self, event):
		
		# Use dpid to differentiate between switches (datapath-id)
		# Each switch has its own flow table. As we'll see in this 
		# example we need to write different rules in different tables.
		dpid = dpidToStr(event.dpid)
		
		switchName = ""
		for m in event.connection.features.ports:
			name = m.name.split("-")
			if switchName == "" :
				switchName = name[0]
			if not switchName == name[0] :
				log.debug("Some Error in mapping name from the OpenFlow Switch Up Message.")

		swID = self.topology.addSwitch(switchName, [])
		
		self.switchMap[switchName] = dpid
		self.switchConnections[swID] = event.connection

		
		# msg = of.ofp_flow_mod()
		# msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
  # 		event.connection.send(msg)

	def findSwitchName(self, dpid) :
		for name in self.switchMap.iterkeys() :
			if self.switchMap[name] == dpid :
				return name

	def getSwitchMacAddr(self, sw) :
		if sw == None : 
			return None
		else : 
			dpid = self.switchMap[sw]
			mac = dpid.replace("-", ":")
			return mac

	def findOutputPort(self, curr, next, prev = None) :
		#curr and next are not adjacent. Find the next switch.
		sw = self.findNeighbour(src = curr, dst = next)
		if sw == prev :
			return of.OFPP_IN_PORT # send back on the input port.

		elif not self.adjacency[self.switchMap[curr]][self.switchMap[sw]] == None :
			return self.adjacency[self.switchMap[curr]][self.switchMap[sw]]
		
		else :	
			print "[ERROR] No edge present."
			return None

	def _handle_LinkEvent (self, event):
		l = event.link
		swdpid1 = dpid_to_str(l.dpid1)
		swdpid2 = dpid_to_str(l.dpid2)

		log.debug ("link %s[%d] <-> %s[%d]",
				   swdpid1, l.port1,
				   swdpid2, l.port2)

		sw1 = self.topology.getSwID(self.findSwitchName(swdpid1))
		sw2 = self.topology.getSwID(self.findSwitchName(swdpid2))

		self.adjacency[sw1][sw2] = int(l.port1)
		self.adjacency[sw2][sw1] = int(l.port2)

		self.topology.addLink(sw1, sw2)

	def _handle_PacketIn (self, event):
		"""
		Handle packet in messages from the switch.
		"""
		packet = event.parsed


		def install_fwdrule(event,srcip,dstip,outport,vlan=0):
			msg = of.ofp_flow_mod()
			
			#Match 
			msg.match = of.ofp_match()
			msg.match.dl_type = ethernet.IP_TYPE
			msg.match.set_nw_src(IPAddr(srcip, 32), 32)
			msg.match.set_nw_dst(IPAddr(dstip, 32), 32)

			
			if not vlan == 0 : 
				# Need to set VLAN Tag for isolation of tenant traffic.
				msg.actions.append(of.ofp_action_vlan_vid(vlan_vid = vlan)) 

			msg.actions.append(of.ofp_action_output(port = outport))


			msg.data = event.ofp
			msg.in_port = event.port
			event.connection.send(msg)

		def installFloodRule(event,packet,outport,vlan=0):
			msg = of.ofp_flow_mod()
			
			#Match 
			msg.match = of.ofp_match.from_packet(packet, event.port)		
			msg.actions.append(of.ofp_action_output(port = outport))
			
			msg.data = event.ofp
			msg.in_port = event.port
			event.connection.send(msg)
		
		def handle_IP_packet (event, packet):
			ip = packet.find('ipv4')
			if ip is None:
				#print "Non IP packet"
				match = of.ofp_match.from_packet(packet)
				if  match.dl_type == packet.ARP_TYPE and match.nw_proto == arp.REQUEST :
					ip = match.nw_dst
					self.respondToARP(ip, packet, match, event)

			else :
				#print ip.__str__() 
				if str(ip.srcip) not in hostMap or str(ip.dstip) not in hostMap :
					return # Ignore packet

				srcSw = self.topology.getSwID(hostMap[str(ip.srcip)])
				dstSw = self.topology.getSwID(hostMap[str(ip.dstip)])


				# Find path from srcSw to dstSw and add rules for ip.srcip and ip.dstip
				self.addForwardingRules(ip.srcip, srcSw, ip.dstip, dstSw)
				#switch is event.dpid
			

		handle_IP_packet(event, packet)

		# flood and install the flow table entry for the flood
	
	def respondToARP(self, ip, packet, match, event):
		# reply to ARP request
		r = arp()
		r.opcode = arp.REPLY
		r.hwdst = match.dl_src
		r.protosrc = ip
		r.protodst = match.nw_src
		r.hwsrc = EthAddr(macMap[str(ip)])
		e = ethernet(type=packet.ARP_TYPE, src=r.hwsrc, dst=r.hwdst)
		e.set_payload(r)
		log.debug("%i %i answering ARP for %s" %
		 ( event.dpid, event.port,
		   str(r.protosrc)))
		msg = of.ofp_packet_out()
		msg.data = e.pack()
		msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
		msg.in_port = event.port
		event.connection.send(msg)

	def addForwardingRules(self, srcip, srcSw, dstip, dstSw, path=[]) :
		if self.checkRouteStatus(srcip, dstip) : return


		print "Adding forwarding rules for", srcip, "->", dstip, ":", srcSw, "->", dstSw
		if path == [] :
			path = self.topology.getPath(srcSw, dstSw) 
		self.printPath(path)

		# Create flow characteristic for flow
		fc = FlowCharacteristic()
		fid = self.fdb.addFlow([srcip, dstip], srcSw, dstSw, fc) # Adding flow to flow database
		self.fdb.changePath(fid, path)
		status = [srcip, dstip, path, fc, fid]
		self.routeStatus.append(status)
		
		for i in range(len(path) - 1) :
			sw1 = path[i]
			sw2 = path[i + 1]

			# add rule to go from sw1 to sw2
			self.addRule(srcip, dstip, sw1, sw2)

		# add flooding rule for dst :
		self.addRule(srcip, dstip, dstSw, None)


	def addRule(self, srcip, dstip, sw1, sw2) : 
		msg = of.ofp_flow_mod()
		connection = self.switchConnections[sw1]
		if sw2 == None : 
			outport = of.OFPP_FLOOD
		else :
			outport = self.adjacency[sw1][sw2]

		#Match 
		msg.match = of.ofp_match()
		msg.match.dl_type = ethernet.IP_TYPE
		msg.match.set_nw_src(IPAddr(srcip, 32), 32)
		msg.match.set_nw_dst(IPAddr(dstip, 32), 32)
		msg.priority = of.OFP_DEFAULT_PRIORITY
		msg.actions.append(of.ofp_action_output(port = outport))

		connection.send(msg)

	def printPath(self, path) :
		namedPath = []
		for i in range(len(path)) : 
			namedPath.append(self.topology.getSwName(path[i]))
		print namedPath

	def checkRouteStatus(self, srcip, dstip) :
		for stat in self.routeStatus : 
			if stat[0] == srcip and stat[1] == dstip : 
				return True
		return False

	def deleteStaleForwardingRules(self,srcip, dstip, path) :
		""" Delete rules for srcip -> dstip on path """
		pass

	def _handle_FlowStatsReceived (self, event):
		#stats = flow_stats_to_list(event.stats)
		swdpid = dpidToStr(event.dpid)
		swID = self.topology.getSwID(self.findSwitchName(swdpid))

		for f in event.stats:
			for stat in self.routeStatus : 
				if f.match.nw_src == stat[0] and f.match.nw_dst == stat[1] and stat[2][0] == swID : 
					# Edge switch for flow. Update Flow Characteristics
					fc = stat[3]
					fc.insert(f.byte_count / 1000, time.time() - self.startTime)
					print "Updating stats:", stat[0], stat[1], swID, f.byte_count / 1000

	# def _handle_PortStatsReceived(self, event) :
	# 	print "Port event"
	# 	swdpid = dpidToStr(event.dpid)
	# 	swID = self.topology.getSwID(self.findSwitchName(swdpid))

	# 	swBytes = 0
	# 	print event.stats
	# 	for f in event.stats:
	# 		print f.port_no, f.tx_bytes, f.rx_bytes
	# 		swBytes += f.rx_bytes - f.tx_bytes 

	# 	print "Updating Switch ", swID, swBytes
	# 	#self.fdb.addSwitchBytes(swID, swBytes)


	def _measurement (self) :
		for connection in self.switchConnections.values():
			connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
			#connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))

	def _scheduler(self) :
		# perform scheduling for events in the current epoch.
		self.fdb.updateCriticalTimes(QUEUE_SIZE)
		

def launch():
	# Run spanning tree so that we can deal with topologies with loops
	pox.openflow.discovery.launch()
	#pox.proto.arp_responder.launch(kw=macMap)
	#pox.forwarding.l2_learning.launch()
	#pox.openflow.spanning_tree.launch()

	'''
	Starting the Topology Slicing module
	'''
	core.registerNew(Scheduler)