#!/usr/bin/python

import socket, argparse


# https://wiki.python.org/moin/TcpCommunication
def main_tcp():
	TCP_IP = "127.0.0.1"
	TCP_PORT = 5006


	print "TCP IP: ", TCP_IP
	print "TCP port: ", TCP_PORT

	s = socket.socket(socket.AF_INET,
						 socket.SOCK_STREAM)

	s.bind((TCP_IP, TCP_PORT))
	s.listen(1)

	conn, addr = s.accept()
	print "Connection addr: ", addr

	while True:
		data = conn.recv(BUFFER_SIZE)
		if not data: break
		print "received data: ", data
		conn.send(data) # echo

	conn.close()


# https://wiki.python.org/moin/UdpCommunication
def main_udp():
	UDP_IP = "127.0.0.1"
	UDP_PORT = 5006


	print "UDP IP: ", UDP_IP
	print "UDP port: ", UDP_PORT

	sock = socket.socket(socket.AF_INET,
						 socket.SOCK_DGRAM)

	sock.bind((UDP_IP, UDP_PORT))

	while True:
		data, addr = sock.recvfrom(1024) # 1024 byte buffer
		print "received message: ", data


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="work_server argument parser")
	parser.add_argument("-u", "--udp", action="store_true", help="use UDP", default=False)
	args = vars(parser.parse_args())

	if(args["udp"]):
		main_udp()

	else:
		main_tcp()