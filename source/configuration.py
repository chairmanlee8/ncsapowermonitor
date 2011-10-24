import json

class Configuration:
	def __init__(self):
		self.db_host = ''
		self.db_port = 0
		self.db_username = ''
		self.db_password = ''
		self.db_database = ''
		self.keep_alive = 0
		self.host = ''
		self.port = 0
		self.devices = {}
		self.instance_variables = {}
		
	def read_config(self, filename):
		f = open(filename, 'r')
		contents = f.read()
		f.close()
		
		obj = json.loads(contents)
		
		self.db_host = str(obj['db_host'])
		self.db_port = int(obj['db_port'])
		self.db_database = str(obj['db_database'])
		self.db_username = str(obj['db_username'])
		self.db_password = str(obj['db_password'])
		self.keep_alive = int(obj['keep_alive_interval'])
		self.host = str(obj['collect_host'])
		self.port = int(obj['collect_port'])
		self.instance_variables = dict(obj['instance_variables'])
		self.devices = dict(obj['device_list'])