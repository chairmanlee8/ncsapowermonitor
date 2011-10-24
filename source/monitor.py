# Simple power monitoring wrapper

import socket
import sys
import os
import time
import random
import threading
import subprocess

from configuration import Configuration

instance_conf = Configuration()
if len(sys.argv) < 3:
	sys.exit("Not enough arguments. Usage: %s <configuration file> ...")
instance_conf.read_config(sys.argv[1])

job_host = socket.gethostname()
job_owner = os.environ.get(instance_conf.instance_variables.get('job_owner'))
job_id = os.environ.get(instance_conf.instance_variables.get('job_id'))
job_process = os.environ.get(instance_conf.instance_variables.get('job_process'))

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send start signal, also start timer thread
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((instance_conf.host, instance_conf.port))
tcp_sock.send('start;%s;%s;%s;%s' % (job_host, job_owner, job_id, job_process))
tcp_sock.recv(1024)
tcp_sock.close()

def timeout():
	tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp_sock.connect((instance_conf.host, instance_conf.port))
	tcp_sock.send('ping')
	tcp_sock.recv(1024)
	tcp_sock.close()

death_timer = threading.Timer(instance_conf.keep_alive / 2, timeout)
death_timer.start()

# Send open marker
udp_sock.sendto("mark;monitor;0", (instance_conf.host, instance_conf.port))

# Execute and block
print "Running executable with power monitoring enabled..."
p = subprocess.Popen(' '.join(sys.argv[2:]), shell=True)
p.wait()
print "...done."

# Send close marker
udp_sock.sendto("mark;monitor;1", (instance_conf.host, instance_conf.port))

# Send stop signal
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((instance_conf.host, instance_conf.port))
tcp_sock.send('stop')
tcp_sock.recv(1024)
tcp_sock.close()