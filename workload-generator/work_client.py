#!/usr/bin/python

import socket, argparse, time, re


class Packet:
	def __init__(self, time, srcip, dstip, length):
		self.time = float(time)
		self.srcip = srcip
		self.dstip = dstip
		self.len = int(length)

	def __str__(self):
		return "Time Sent: {}\t SrcIP: {}\t DstIP: {}\t Len: {}\t".format(self.time, self.srcip, self.dstip, self.len)


# https://wiki.python.org/moin/TcpCommunication
def main_tcp(bytesToSend, ip):
	TCP_IP = ip
	TCP_PORT = 5006
	BUFFER_SIZE = 1024
	MESSAGE = "Hello World!"

	print "UDP IP: ", UDP_IP
	print "UDP port: ", UDP_PORT
	print "message: ", MESSAGE


	# Create TCP socket
	s = socket.socket(socket.AF_INET, 
						 socket.SOCK_STREAM)
	
	# Connect to TCP server
	s.connect((TCP_IP, TCP_PORT))


	# Send bytesToSend# of bytes
	for i in range(bytesToSend):
		s.send(MESSAGE)
		data = s.recv(BUFFER_SIZE)
		print "received reply: ", data

	# Close TCP connection        
	s.close()



# https://wiki.python.org/moin/UdpCommunication
def main_udp(bytesToSend, ip):
	UDP_IP = ip
	UDP_PORT = 5005
	MESSAGE = "A"

	print "UDP IP: ", UDP_IP
	print "UDP port: ", UDP_PORT
	print "message: ", MESSAGE
	print "#bytes: ", bytesToSend

	# Create UDP socket
	sock = socket.socket(socket.AF_INET, 
						 socket.SOCK_DGRAM)
	

	# Send #bytesToSend TCP packets
	for i in range(bytesToSend):
		sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
		time.sleep(0.0001)



# Parse tracefile into packets to send
def parse(tracefile):
	Packets = []
	with open(tracefile, 'r') as f:
		for line in f:
			line_split = line.split(" ")
			#print line_split

			# Packet #
			pkt_num = line_split[0]

			# Send time (will be used as delta w/ the next one)
			pkt_sendtime = line_split[1]	

			# SRC and DST IPs
			pkt_srcip = line_split[2]
			pkt_dstip = line_split[4]

			# pkt length
			p = re.compile('Len=(\d+)')
			pkt_len = p.findall(line)[0]

			# just in case
			if not pkt_len:
				pkt_len = 0

			pkt = Packet(pkt_sendtime, pkt_srcip, pkt_dstip, pkt_len) 

			Packets.append(pkt)

	return Packets


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="work_client argument parser")
	#parser.add_argument("-u", "--udp", help="use UDP", default=False)
	parser.add_argument("-b", "--bytes", help="#bytes to send", default=4096)
	parser.add_argument("-ip", "--ip", help="IP address to send to", default="127.0.0.1")
	parser.add_argument("-t", "--trace", help="trace file to use (.txt)", default="")


	# parse all CL args
	args = vars(parser.parse_args())
	   

	# get #bytes to send from the args (this will be phased out once trace files work)
	bytesToSend = int(args["bytes"])

	# create all of the packets to send based on trace file
	# will be a list of Packet objects
	pktsToSend = parse(args["trace"])
	

	# Send all of the packets, then sleep for the delta between two packets
	for i, packet in enumerate(pktsToSend):

		#if(args["udp"]):
		main_udp(packet.len, packet.dstip)

		#else:
		#	main_tcp(packet.len, packet.dstip)

		# Sleep for delta 

		if i < len(pktsToSend)-1:
			delta = pktsToSend[i+1].time - pktsToSend[i].time
			#print "Sleeping for... ", delta
			time.sleep(delta / 1000)
