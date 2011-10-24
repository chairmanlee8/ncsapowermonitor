import collections
import serial
import atexit
import copy
import sys
import os
import threading
import random
import socket
import time

import SocketServer
import MySQLdb

from configuration import Configuration
from device import ReadDeviceThread, BufferConsumer, MAX_BUFFER
from timestamp import *

from debug_print import debug_print

BUFFER_UP_TIME = 5

instance_conf = Configuration()
device_handle = serial.Serial()
device_thread = ReadDeviceThread()
data_buffer = {}	# device_name: device_deque
data_buffer_lock = threading.RLock()
marker_up_buffer = []
last_buffer_up = time.time()
marker_buffer = []	# (marker_time, marker_name, marker_type)
marker_buffer_lock = threading.RLock()
guid = 0
db = None
db_cursor = None

# (UDP) Data Collection/Marks Server

def process_marker_buffer():
	global marker_up_buffer
	global db_cursor
	
	debug_print("Upping %d markers..." % len(marker_up_buffer))

	for marker in marker_up_buffer:
		u, m = split_timestamp(marker[0])
		db_cursor.execute("""INSERT INTO marker_data (guid, time_unix, time_ms, name, marker_type)
			VALUES (%s,%s,%s,%s,%s)""", (guid, u, m, marker[1], marker[2]))

	db.commit()
	marker_up_buffer = []

def upload_markers(override):
	global marker_buffer
	global marker_up_buffer
	global marker_buffer_lock
	global last_buffer_up

	with marker_buffer_lock:
		if override or len(marker_buffer) > MAX_BUFFER or (time.time() - last_buffer_up) > BUFFER_UP_TIME:
			last_buffer_up = time.time()

			marker_up_buffer = copy.copy(marker_buffer)
			marker_buffer = []

			# Spawn buffer upload thread
			t = threading.Thread(target=process_marker_buffer)
			t.start()

class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		global marker_buffer
		global marker_buffer_lock

		data = self.request[0].strip().split(';')
		
		try:
			if data[0] == 'mark':
				with marker_buffer_lock:
					marker_buffer += [(time.time(), data[1], int(data[2]))]

				upload_markers(False)
		except IndexError:
			debug_print("Malformed request: %s" % data)
			
class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
	pass
	
# (TCP) Keep-alive and Critical Requests Server

def timeout():
	debug_print("No ping for %d seconds, timeout." % instance_conf.keep_alive)
	# Upload markers and pause
	upload_markers(True)
	device_thread.pause()

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		global device_thread
		global guid
		
		if not hasattr(self, 'death_timer'):
			debug_print("Starting death timer interval %d seconds" % (instance_conf.keep_alive,))
			self.death_timer = threading.Timer(instance_conf.keep_alive, timeout)
			self.death_timer.start()
		
		data = self.request.recv(1024).strip().split(';')
		
		try:
			if data[0] == 'start':
				guid = int(random.getrandbits(32))
				
				job_host = data[1]
				job_owner = data[2]
				job_id = data[3]
				job_process = data[4]

				db_cursor.execute("""INSERT INTO job_data (guid, job_started, job_host, job_owner, job_id, job_process) 
					VALUES (%s,NOW(),%s,%s,%s,%s)""", (guid, job_host, job_owner, job_id, job_process))
				
				for device_name, sensors in instance_conf.devices.iteritems():
					for sensor in sensors:
						db_cursor.execute("""INSERT INTO conf_data_sensor (guid, device_sensor, voltage, description)
							VALUES (%s,%s,%s,%s)""", (guid, device_sensor(device_name, sensor), sensor['voltage'], sensor['description']))
				
				db.commit()
				
				device_thread.unpause()
			elif data[0] == 'ping':
				if self.death_timer is not None:
					self.death_timer.cancel()
					self.death_timer = threading.Timer(instance_conf.keep_alive, timeout)
					self.death_timer.start()
			elif data[0] == 'stop':
				# Up the rest of the markers and pause
				upload_markers(True)
				device_thread.pause()
				
			self.request.send("Command processed.")
		except IndexError:
			estr = "Malformed request: %s" % data
			self.request.send(estr)
			debug_print(estr)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass
	
# Main loop

@atexit.register
def cleanup():
	debug_print("Closing devices and database...")
	
	device_handle.close()
	db_cursor.close()

if __name__ == "__main__":
	if len(sys.argv) < 3:
		sys.exit("Not enough arguments. Usage: %s <configuration file> <device name>")
		
	random.seed()
	
	instance_conf.read_config(sys.argv[1])
	
	# Open database
	db = MySQLdb.connect(host=instance_conf.db_host, port=instance_conf.db_port, db=instance_conf.db_database, user=instance_conf.db_username, passwd=instance_conf.db_password)
	db_cursor = db.cursor()
	
	# Open device
	device_handle = serial.Serial(sys.argv[2])
	
	device_thread.set_device_handle(device_handle)
	device_thread.set_data_buffer(data_buffer)
	device_thread.set_data_buffer_lock(data_buffer_lock)
	device_thread.start()

	debug_print("Device running in thread: %s" % device_thread.getName())

	# Open consumer
	consumer = BufferConsumer(consume_period=3, data_buffer=data_buffer, data_buffer_lock=data_buffer_lock, db_connection=db, instance_config=instance_conf)
	consumer.start()

	debug_print("Consumer running in thread: %s" % consumer.getName())
	
	# Start TCP service
	tcp_server = ThreadedTCPServer((instance_conf.host, instance_conf.port), ThreadedTCPRequestHandler)
	
	tcp_server_thread = threading.Thread(target=tcp_server.serve_forever)
	tcp_server_thread.setDaemon(True)
	tcp_server_thread.start()
	
	debug_print("TCP server running in thread: %s" % tcp_server_thread.getName())

	# Start UDP service
	udp_server = ThreadedUDPServer((instance_conf.host, instance_conf.port), ThreadedUDPRequestHandler)

	udp_server_thread = threading.Thread(target=udp_server.serve_forever)
	udp_server_thread.setDaemon(True)
	udp_server_thread.start()

	debug_print("UDP server is running in thread: %s" % udp_server_thread.getName())
	
	# Wait for all threads to exit
	
	udp_server_thread.join()
	tcp_server_thread.join()
	consumer.join()
	device_thread.join()
	
	sys.exit()
