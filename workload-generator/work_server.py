#!/usr/bin/python

import socket, argparse


# https://wiki.python.org/moin/TcpCommunication
def main_tcp(bytes_expected, ip):
	TCP_IP = ip
	TCP_PORT = 5006


	print "TCP IP: ", TCP_IP
	print "TCP port: ", TCP_PORT


	# Create TCP socket
	s = socket.socket(socket.AF_INET,
						 socket.SOCK_STREAM)

	# Bind to TCP_PORT to listen for client connections
	s.bind((TCP_IP, TCP_PORT))
	s.listen(1)

    # numMessages = 0

	conn, addr = s.accept()
	print "Connection addr: ", addr

	while True:
		data = conn.recv(BUFFER_SIZE)
		if not data: break
		print "received data: ", data
		conn.send(data) # echo
                # numMessages += 1

                # if numMessages == bytes_expected:
                #         print "No data loss from client"
                #         break
                
	conn.close()


# https://wiki.python.org/moin/UdpCommunication
def main_udp(bytes_expected, ip):
	UDP_IP = ip
	UDP_PORT = 5005


	print "UDP IP: ", UDP_IP
	print "UDP port: ", UDP_PORT

	# Create UDP socket
	sock = socket.socket(socket.AF_INET,
						 socket.SOCK_DGRAM)

	# Bind to UDP_PORT
	sock.bind((UDP_IP, UDP_PORT))

	# messagecount = 1

	while True:
		data, addr = sock.recvfrom(1024) # 1024 byte buffer
		print "received message: ", data
		# messagecount += 1

		# if messagecount == bytes_expected:
		# 	print "No packet loss.."
		# 	exit(0)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="work_server argument parser")
	#parser.add_argument("-u", "--udp", action="store_true", help="use UDP", default=False)
	#parser.add_argument("-b", "--bytes", help="#bytes expected", default=4096)
    parser.add_argument("-ip", "--ip", help="IP address to recv from", default="127.0.0.1")
    #parser.add_argument("-t", "--trace", help="trace file to use (.txt)", default="")


	args = vars(parser.parse_args())
    bytes_expected = int(args["bytes"])

	#if(args["udp"]):
	main_udp(bytes_expected, args["ip"])

	#else:
	#	main_tcp(bytes_expected, args["ip"])
