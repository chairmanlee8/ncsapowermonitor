import socket
import sys
import time
import random

from configuration import Configuration

instance_conf = Configuration()
if len(sys.argv) <= 1:
	sys.exit("Not enough arguments. Usage: %s <configuration file>")
instance_conf.read_config(sys.argv[1])

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print "CTRL-BREAK to quit. Commands are:"
print "start"
print "mark <name> <type>"
print "ping"
print "stop"

while 1:
	command = raw_input('> ').split(' ')
	
	if command[0] == 'start':
		tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcp_sock.connect((instance_conf.host, instance_conf.port))
		tcp_sock.send('start')
		print tcp_sock.recv(1024)
		tcp_sock.close()
	elif command[0] == 'stop':
		tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcp_sock.connect((instance_conf.host, instance_conf.port))
		tcp_sock.send('stop')
		print tcp_sock.recv(1024)
		tcp_sock.close()
	elif command[0] == 'mark':
		udp_sock.sendto("mark;%s;%d" % (command[1], int(command[2])), (instance_conf.host, instance_conf.port))
	elif command[0] == 'ping':
		tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcp_sock.connect((instance_conf.host, instance_conf.port))
		tcp_sock.send('ping')
		print tcp_sock.recv(1024)
		tcp_sock.close()
	else:
		print 'Unrecognized command.'