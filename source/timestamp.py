def split_timestamp(ft):
	return (int(ft), int(1000*(ft-int(ft))))
	
def join_timestamp(it, mt):
	return float(it) + float(mt)/1000.0

def device_sensor(device_name, sensor):
	return ("%s_%d" % (device_name, int(dict(sensor)['io_port'])))