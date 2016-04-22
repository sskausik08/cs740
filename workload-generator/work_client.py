#!/usr/bin/python

import socket, argparse, time


# https://wiki.python.org/moin/TcpCommunication
def main_tcp():
	TCP_IP = "127.0.0.1"
	TCP_PORT = 5006
	BUFFER_SIZE = 1024
	MESSAGE = "Hello World!"

	print "UDP IP: ", UDP_IP
	print "UDP port: ", UDP_PORT
	print "message: ", MESSAGE

	s = socket.socket(socket.AF_INET, 
						 socket.SOCK_STREAM)
	
	s.connect((TCP_IP, TCP_PORT))
	s.send(MESSAGE)
	data = s.recv(BUFFER_SIZE)
	s.close()

	print "received data: ", data


# https://wiki.python.org/moin/UdpCommunication
def main_udp(bytesToSend):
	UDP_IP = "127.0.0.1"
	UDP_PORT = 5005
	MESSAGE = "A"

	print "UDP IP: ", UDP_IP
	print "UDP port: ", UDP_PORT
	print "message: ", MESSAGE
	print "#bytes: ", bytesToSend

	sock = socket.socket(socket.AF_INET, 
						 socket.SOCK_DGRAM)
	
	for i in range(bytesToSend):
		sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
		time.sleep(0.0001)



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="work_client argument parser")
	parser.add_argument("-u", "--udp", help="use UDP", default=True)
	parser.add_argument("-b", "--bytes", help="#bytes to send", default=4096)

	args = vars(parser.parse_args())

	if(args["udp"]):
		main_udp(int(args["bytes"]))

	else:
		main_tcp()