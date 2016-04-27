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



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="work_client argument parser")
	parser.add_argument("-u", "--udp", help="use UDP", default=False)
	parser.add_argument("-b", "--bytes", help="#bytes to send", default=4096)
    parser.add_argument("-ip", "--ip", help="IP address to send to", default="127.0.0.1")
    parser.add_argument("-t", "--trace", help="trace file to use (.txt)", default="")


	args = vars(parser.parse_args())
       
        bytesToSend = int(args["bytes"])
        
	if(args["udp"]):
		main_udp(bytesToSend, args["ip"])

	else:
		main_tcp(bytesToSend, args["ip"])
