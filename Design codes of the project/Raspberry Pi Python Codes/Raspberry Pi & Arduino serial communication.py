import serial
import time

ser=serial.Serial("/dev/ttyACM0", 9600)
ser.baudrate=9600
ser.flushInput()
ser.flushOutput()
orientation=1
orientationTemp= str(orientation)
sent = 0

if orientation > 0:
	while True:
		if sent==0 :
			time.sleep(2)
			ser.write(orientationTemp)
			time.sleep(.1)
			sent=1
		time.sleep(.1)
		read_ser = ser.readline(ser.inWaiting())
		print(read_ser)	

		if read_ser == orientationTemp: #orientationTemp
			print("data sent")
			break

	while True:
		com= ser.readline(ser.inWaiting())
		time.sleep(0.1)
		print(com)
		if com == "complete":
			break

	