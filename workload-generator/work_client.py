#!/usr/bin/python

import socket, argparse, time


# https://wiki.python.org/moin/TcpCommunication
def main_tcp(bytesToSend, ip):
	TCP_IP = ip
	TCP_PORT = 5006
	BUFFER_SIZE = 1024
	MESSAGE = "Hello World!"

	print "UDP IP: ", UDP_IP
	print "UDP port: ", UDP_PORT
	print "message: ", MESSAGE

	s = socket.socket(socket.AF_INET, 
						 socket.SOCK_STREAM)
	
	s.connect((TCP_IP, TCP_PORT))

        for i in range(bytesToSend):
                s.send(MESSAGE)
                data = s.recv(BUFFER_SIZE)
                print "received reply: ", data
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

	sock = socket.socket(socket.AF_INET, 
						 socket.SOCK_DGRAM)
	
	for i in range(bytesToSend):
		sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
		time.sleep(0.0001)



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="work_client argument parser")
	parser.add_argument("-u", "--udp", help="use UDP", default=True)
	parser.add_argument("-b", "--bytes", help="#bytes to send", default=4096)
        parser.add_argument("-ip", "--ip", help="IP address to send to", default="127.0.0.1")

	args = vars(parser.parse_args())
       
        bytesToSend = int(args["bytes"])
        
	if(args["udp"]):
		main_udp(bytesToSend, args["ip"])

	else:
		main_tcp(bytesToSend, args["ip"])
