import serial
import sys

if len(sys.argv) < 2:
	print "Not enough arguments. Usage: %s <device>"
	sys.exit()

ser = serial.Serial(sys.argv[1])

try:
	while 1:
		print ser.readline()
except KeyboardInterrupt:
	ser.close()