import time
import threading
import collections

from timestamp import *
from debug_print import debug_print

MAX_BUFFER = 50

class BufferConsumer(threading.Thread):
	def __init__(self, **kwargs):
		threading.Thread.__init__(self)

		if 'consume_period' in kwargs:
			self.set_consume_period(kwargs['consume_period'])
		if 'data_buffer' in kwargs:
			self.set_data_buffer(kwargs['data_buffer'])
		if 'data_buffer_lock' in kwargs:
			self.set_data_buffer_lock(kwargs['data_buffer_lock'])
		if 'db_connection' in kwargs:
			self.set_db_connection(kwargs['db_connection'])
		if 'instance_config' in kwargs:
			self.set_instance_config(kwargs['instance_config'])

	def set_consume_period(self, p): self.consume_period = p
	def set_data_buffer(self, buf):	self.data_buffer = buf
	def set_data_buffer_lock(self, lk): self.data_buffer_lock = lk
	def set_db_connection(self, conn): self.db = conn
	def set_instance_config(self, c): self.instance_config = c

	def run(self):
		# Consume everything in the data buffer
		while 1:
			with self.data_buffer_lock:
				cur = self.db.cursor()

				for device_name, data in self.data_buffer.iteritems():
					# Is this device even being recorded?
					if device_name not in self.instance_config.devices:
						continue

					while len(data) > 0:
						datum = data.pop()

						for sensor in self.instance_config.devices[device_name]:
							t, a = datum
							u, m = split_timestamp(t)
							cur.execute("""INSERT INTO power_data (device_sensor, time_unix, time_ms, amperage)
								VALUES (%s,%s,%s,%s)""", (device_sensor(device_name, sensor), u, m, a[sensor['io_port']]))

				self.db.commit()

			time.sleep(self.consume_period)
			

class ReadDeviceThread(threading.Thread):
	def __init__(self, **kwargs):
		threading.Thread.__init__(self)
		
		self._stop = threading.Event()
		self._notpause = threading.Event()
		self._notpause.clear()
		
		if 'device_handle' in kwargs:
			self.set_device_handle(kwargs['device_handle'])
		if 'data_buffer' in kwargs:
			self.set_data_buffer(kwargs['data_buffer'])
		if 'data_buffer_lock' in kwargs:
			self.set_data_buffer_lock(kwargs['data_buffer_lock'])
		
	def set_device_handle(self, ser): self.ser = ser
	def set_data_buffer(self, buf):	self.data_buffer = buf
	def set_data_buffer_lock(self, lk): self.data_buffer_lock = lk
	
	def stop(self):	self._stop.set()
	def stopped(self): return self._stop.isSet()
	
	def pause(self): self._notpause.clear()
	def unpause(self): 
		self.ser.flushInput()	# Flush the input buffer to discard old events
		self.initializing = True
		self._notpause.set()
	def paused(self): return not self._notpause.isSet()
		
	def run(self):
		line_buffer = collections.deque(maxlen=10)
		self.initializing = True
		device_file = self.ser.port
		
		while not self._stop.isSet():
			self._notpause.wait()
			
			line = self.ser.readline()
			
			# Read lines continuously; ser.readline() will block until a line is read.
			# Wait for first "analogzero=" line
			# Once encountered, consider the state to be initialized -- ser.readline() will now be piped into line_buffer FIFO
			# Wait for "analogzero=" line
			# Once encountered, we know that we have read in one page of data
			# Parse that page of data and pipe into data_buffer FIFO
			
			if self.initializing:
				if "analogzero" in line:
					self.initializing = False
			else:
				if "analogzero" in line:
					# empty buffer and push to device data buffer
					with self.data_buffer_lock:
						if device_file not in self.data_buffer:
							self.data_buffer[device_file] = collections.deque(maxlen=MAX_BUFFER)
						
					try:
						line_buffer.pop()	# pop off trailing \r\n
					except IndexError:
						continue
					
					if len(line_buffer) > 0:
						channels_data = []
						t = time.time()
						while len(line_buffer) > 0:
							try:
								x = line_buffer.pop()
								channels_data.insert(0, float(x.split('=')[1]))
							except IndexError:
								debug_print("Possible malformed data.")
								channels_data.insert(0, 0.0)
							
						with self.data_buffer_lock:
							self.data_buffer[device_file].append((t, channels_data))

						debug_print("Data buffer for %s is size %d." % (device_file, len(self.data_buffer[device_file])))
				else:		
					line_buffer.append(line)