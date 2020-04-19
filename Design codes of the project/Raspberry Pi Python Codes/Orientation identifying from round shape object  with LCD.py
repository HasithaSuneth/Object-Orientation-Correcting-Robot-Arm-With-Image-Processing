from imutils.video import VideoStream
from matplotlib import pyplot as plt
from RPLCD.gpio import CharLCD
from collections import deque
import RPi.GPIO as GPIO
import numpy as np
import cv2 as cv
import imutils
import time

def main():
	#GPIO.setwarnings(False)
	GPIO.setup(17, GPIO.IN)
	GPIO.setup(27, GPIO.IN)
	GPIO.setup(22, GPIO.IN)
	GPIO.setup(23, GPIO.OUT)
	normalHigh = 0
	runHigh = 0
	autorunHigh = 0
	autoCount = 0
	resetHigh = 0
	option = 0
	lcdmain = 0

	lcd.cursor_pos = (0, 2)
	lcd.write_string('Orientation')
	lcd.cursor_pos = (1, 0)
	lcd.write_string('Correction R.Arm')
	time.sleep(3)
	lcd.clear()
	lcd.cursor_pos = (0, 3)
	lcd.write_string('Main Menu')
	lcd.cursor_pos = (1, 5)
	lcd.write_string('Press:')
	time.sleep(2)

	def mainLCD():
		lcd.clear()
		lcd.write_string('1.TakeDefAngle')
		lcd.cursor_pos = (1, 0)
		lcd.write_string('2.Start 3.Stop')

	def TakeDefAngleLCD():
		lcd.clear()
		lcd.cursor_pos = (0, 2)
		lcd.write_string('Capturing...')
		lcd.cursor_pos = (1, 1)
		lcd.write_string('Default Angle')

	def resetLCD():
		lcd.clear()
		lcd.cursor_pos = (0, 2)
		lcd.write_string('Turning Off')
		lcd.cursor_pos = (1, 3)
		lcd.write_string('.........')

	def manualLCD():
		lcd.clear()
		lcd.cursor_pos = (0, 2)
		lcd.write_string('Manual Mode')

	def autoLCD():
		lcd.clear()
		lcd.cursor_pos = (0, 3)
		lcd.write_string('Auto Mode')

	def indicater():
		GPIO.output(23, GPIO.HIGH)
		time.sleep(0.2)
		GPIO.output(23, GPIO.LOW)
		time.sleep(0.2)

	mainLCD()
	while True:
		indicater()	# Indicater LED
		if lcdmain == 1:
			mainLCD()
			lcdmain = 0

		if GPIO.input(17) and normalHigh==0:
			normalHigh=1
		
		if GPIO.input(27)== GPIO.HIGH and runHigh==0:
			runHigh=1

		if GPIO.input(27)== GPIO.HIGH:
			autorunHigh = autorunHigh + 1
			
		if GPIO.input(22)== GPIO.HIGH and resetHigh==0:
			if autorunHigh >= 6:
				autorunHigh = 0
				autoCount = 0
				resetHigh = 2
			else:
				resetHigh=1

		if GPIO.input(22)== GPIO.LOW and resetHigh==2:
			resetHigh=0
			
		if GPIO.input(17)== GPIO.LOW and normalHigh==1:	# Default image take button
			normalHigh=0
			TakeDefAngleLCD()
			get_original_image()
			lcdmain = 1

		if GPIO.input(22)== GPIO.LOW and resetHigh==1:	# Stop & Reset button
			resetHigh=0
			resetLCD()
			GPIO.cleanup()
			break

		if GPIO.input(27)== GPIO.LOW and runHigh==1 or autorunHigh >= 6:	# Mode button
			runHigh=0
			if autorunHigh < 6:
				autorunHigh=0
			else :
				autoCount = autoCount + 1
			if autorunHigh >= 6:
				autoLCD()
			else :
				manualLCD()

			identify_object(autoCount)
			lcdmain = 1

def get_original_image():

	def crop ():
		img1 = cv.imread('images_temp/normal_img.jpg')
		edged = cv.Canny(img1, 0, 200)
		pts = np.argwhere(edged>0)
		y1, x1 = pts.min(axis=0)
		y2, x2 = pts.max(axis=0)
		croppedimg2 = img1[y1:y2, x1:x2]
		cv.imwrite(filename='images_temp/normal_crop_img.jpg', img=croppedimg2)		

	def capture ():
		GPIO.output(24, GPIO.HIGH)	# Flash Light On
		time.sleep(2)
		frame = vs.read()	# Capturing Image
		GPIO.output(24, GPIO.LOW)	# Flash Light Off
		frame = frame[0:479, 0:639]	# remove white line(bug fix)
		cv.imwrite(filename='images_temp/normal_img.jpg', img=frame)	# Write on SD card
		time.sleep(.1)

	capture()
	try: 
		crop()
	except Exception as e:
		print("Picture is not clear, can't crop ",e)
	

def identify_object(auto):
	def image_identify():
		cupLower = (0, 100, 100)	# Lower color range for color identification
		cupUpper = (100, 255, 255)	# Higher color range for color identification
		pts = deque(maxlen=32)
		key1=0

		while True:
			frame = vs.read()	# Read Live feed
			frame = imutils.resize(frame, width=600)	# Resize frame
			blurred = cv.GaussianBlur(frame, (11, 11), 0)	# Blurred image 
			hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)	# Convert into HSV color format

			mask = cv.inRange(hsv, cupLower, cupUpper)	# Creat mask
			mask = cv.erode(mask, None, iterations=2)
			mask = cv.dilate(mask, None, iterations=2)
			cnts = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
			cnts = imutils.grab_contours(cnts)
			center = None

			if len(cnts) <= 0:
				key1=0

			if len(cnts) > 0:	# if object centerd
				print("detect")
				c = max(cnts, key=cv.contourArea)
				((x, y), radius) = cv.minEnclosingCircle(c)
				M = cv.moments(c)
				center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
				if center >= (300, 220) and center <= (320, 240):
					key1 = key1+1
					time.sleep(1)
					if key1 == 5:
						cv.imwrite(filename='images_temp/saved_img.jpg', img=frame)
						print("Image captured")
						cv.destroyAllWindows()
						import orientation
						break

	def distance_identify(auto):
		TRIG = 4	# Ultrasonic Sensor Triger pin configeration
		ECHO = 18	# Ultrasonic Sensor Echo pin configeration
		GPIO.setup(TRIG, GPIO.OUT)
		GPIO.setup(ECHO, GPIO.IN)
		GPIO.setup(22, GPIO.IN)
		key1=0
		lcd.cursor_pos = (1, 0)
		lcd.write_string('Object Detecting')	# LCD Display print

		while True:
			GPIO.output(TRIG, True)	# Triger pin On
			time.sleep(0.0001)		
			GPIO.output(TRIG, False) # Triger pin Off

			while GPIO.input(ECHO) == False:
				start = time.time()
			while GPIO.input(ECHO) == True:
				end = time.time()
			sig_time = end-start
			distance = sig_time / 0.000058
			if int(distance) < 15:	# Identify nearby object
				key1 = key1+1	# Variable use for conform object statues
				time.sleep(1)
				if key1 == 5 and auto <=1:
					lcd.cursor_pos = (1, 0)
					lcd.write_string('Object Detected ')
					GPIO.output(24, GPIO.HIGH)	# Flash Light On
					time.sleep(2)
					frame = vs.read()	# Capture Image
					GPIO.output(24, GPIO.LOW)	# Flash Light Off
					frame = frame[0:479, 0:639]
					cv.imwrite(filename='images_temp/saved_img.jpg', img=frame)	# Image save on SD Card
					time.sleep(.1)
					print("image captured")
					orientation()	# Call object orientation finding Funtion
					break
				
			if int(distance) > 15:	# Use for Auto Mode
				key1 = 0
				if auto > 1:
					auto = 1

			if GPIO.input(22)== GPIO.HIGH:	# Go back to main menu
				break
	distance_identify(auto)
	#image_identify()

def orientation():
	rotation_ratio = 360 # 180, 72
	angles=1 # 2, 5
	
	myList=[None]*rotation_ratio	# List data structure for Rotated mask
	blackPixList=[None]*rotation_ratio	# List data structure for Subtract result
	differList=[None]*rotation_ratio	# List data structure for Sum of black pixels count
	i=0

	lower=[(0, 100, 100)] # Lower color range for color identification
	upper=[(100, 255, 255)] # Higher color range for color identification

	img1 = cv.imread('images_temp/normal_crop_img.jpg')	# Load Default image
	img2 = cv.imread('images_temp/saved_img.jpg')	# Load Rotated image

	edged = cv.Canny(img2, 0, 200) # Canny edge detection algorithm
	pts = np.argwhere(edged>0)
	y1, x1 = pts.min(axis=0)
	y2, x2 = pts.max(axis=0)
	croppedimg2 = img2[y1:y2, x1:x2]

	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")

	mask1 = cv.inRange(img1, lower, upper)	# Create mask for Default image
	mask2 = cv.inRange(croppedimg2, lower, upper) # Create mask for Rotated image

	img_shape1 = img1.shape
	img_shape2 = croppedimg2.shape

	if img_shape1[0]> img_shape2[0] or img_shape1[0] == img_shape2[0]:	# Get both masks into same shape
		if img_shape1[1]>img_shape2[1] or img_shape1[1]==img_shape2[1]:
			crop_mask1 = mask1[0:img_shape2[0], 0:img_shape2[1]]
			crop_mask2 = mask2[0:img_shape2[0], 0:img_shape2[1]]
		if img_shape1[1]<img_shape2[1]:
			crop_mask1 = mask1[0:img_shape2[0], 0:img_shape1[1]]
			crop_mask2 = mask2[0:img_shape2[0], 0:img_shape1[1]]
	elif img_shape1[0]< img_shape2[0]:
		if img_shape1[1]>img_shape2[1] or img_shape1[1]==img_shape2[1]:
			crop_mask1 = mask1[0:img_shape1[0], 0:img_shape2[1]]
			crop_mask2 = mask2[0:img_shape1[0], 0:img_shape2[1]]
		if img_shape1[1]<img_shape2[1]:
			crop_mask1 = mask1[0:img_shape1[0], 0:img_shape1[1]]
			crop_mask2 = mask2[0:img_shape1[0], 0:img_shape1[1]]


	for angle in np.arange(0, 360, angles):	# Rotate mask2 image and save it in List
		myList[int(i)]= imutils.rotate(crop_mask2, angle)
		i=i+1

	for a in range(len(myList)):	# Subtract mask1 image with Rotated image List
		differList[a] = cv.subtract(crop_mask1, myList[a])	

	for b in range(len(myList)):	# Count sum of black pixels
		blackPixList[b]=np.sum(differList[b]==0)

	orientaionValue = (blackPixList.index(max(blackPixList)))*angles	# Use highest black pixel count index for get correct angel
	lcd.cursor_pos = (1, 0)
	lcd.write_string('Orientation:    ')
	lcd.cursor_pos = (1, 12)
	lcd.write_string(str(orientaionValue))
	time.sleep(2)
	print("max ", max(blackPixList), "index ", blackPixList.index(max(blackPixList)))
	print("orientation :", (blackPixList.index(max(blackPixList)))*angles)
	cv.imwrite('images_temp/mask1.jpg', crop_mask1)
	cv.imwrite('images_temp/mask2.jpg', crop_mask2)
	cv.imwrite('images_temp/mask_final.jpg', myList[blackPixList.index(max(blackPixList))])
	
vs = VideoStream(src=0).start()
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
lcd = CharLCD(cols=16, rows=2, pin_rs=5, pin_e=6, pins_data=[13, 19, 26, 21],numbering_mode=GPIO.BCM)	# LCD Configuration
main()