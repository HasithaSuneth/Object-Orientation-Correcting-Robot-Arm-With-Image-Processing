from imutils.video import VideoStream
from matplotlib import pyplot as plt
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

	def indicater():
		GPIO.output(23, GPIO.HIGH)
		time.sleep(0.2)
		GPIO.output(23, GPIO.LOW)
		time.sleep(0.2)

	while True:
		indicater()
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
			
		if GPIO.input(17)== GPIO.LOW and normalHigh==1:
			normalHigh=0
			get_original_image()

		if GPIO.input(22)== GPIO.LOW and resetHigh==1:
			resetHigh=0
			GPIO.cleanup()
			break

		if GPIO.input(27)== GPIO.LOW and runHigh==1 or autorunHigh >= 6:
			runHigh=0
			if autorunHigh < 6:
				autorunHigh=0
			else :
				autoCount = autoCount + 1
			identify_object(autoCount)
			#break

def get_original_image():

	def crop ():
		img1 = cv.imread('images_temp/normal_img.jpg')
		#gray = cv.cvtColor(img1, cv.COLOR_BGR2GRAY) #img1
		#gray = cv.GaussianBlur(gray, (3, 3), 0)  # (gray, (3, 3), 0)
		edged = cv.Canny(img1, 0, 200) # 150 550 gray
		cv.imwrite("images_temp/edge.jpg", edged) # check crop details
		pts = np.argwhere(edged>0)
		y1, x1 = pts.min(axis=0)
		y2, x2 = pts.max(axis=0)
		croppedimg2 = img1[y1:y2, x1:x2]
		cv.imwrite(filename='images_temp/normal_crop_img.jpg', img=croppedimg2)		

	def capture ():
		#vs = VideoStream(src=0).start()
		GPIO.output(24, GPIO.HIGH)
		time.sleep(2)
		frame = vs.read()
		GPIO.output(24, GPIO.LOW)
		frame = frame[0:479, 0:639] # remove white line 
		cv.imwrite(filename='images_temp/normal_img.jpg', img=frame)
		time.sleep(.1)

	capture()
	try: 
		crop()
	except Exception as e:
		print("Picture is not clear, can't crop ",e)
	

def identify_object(auto):
	def image_identify():
		#vs = VideoStream(src=0).start()
		cupLower = (100, 100, 20)	 # blue color
		cupUpper = (130, 255, 255)	
		pts = deque(maxlen=32)
		key1=0

		while True:
			frame = vs.read()
			frame = imutils.resize(frame, width=600)
			blurred = cv.GaussianBlur(frame, (11, 11), 0)
			hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

			mask = cv.inRange(hsv, cupLower, cupUpper)
			mask = cv.erode(mask, None, iterations=2)
			mask = cv.dilate(mask, None, iterations=2)
			cnts = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
			cnts = imutils.grab_contours(cnts)
			center = None

			if len(cnts) <= 0:
				key1=0

			#if GPIO.input(channel 2):
				#break

			if len(cnts) > 0:
				print("detect")
				c = max(cnts, key=cv.contourArea)
				((x, y), radius) = cv.minEnclosingCircle(c)
				M = cv.moments(c)
				center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
				if radius > 10: # Remove after test......
					cv.circle(frame, (int(x), int(y)), int(radius),	(0, 255, 255), 2)
					cv.circle(frame, center, 5, (0, 0, 255), -1)
					pts.appendleft(center) # ........
				if center >= (300, 220) and center <= (320, 240):
					key1 = key1+1
					time.sleep(1)
					if key1 == 5:
						cv.imwrite(filename='images_temp/saved_img.jpg', img=frame)
						print("Image captured")
						cv.destroyAllWindows()
						import orientation
						break
			#key = cv.waitKey(1)
			#if key == ord('q'):
				#break
			#cv.imshow("Capturing", frame)

	def distance_identify(auto):
		TRIG = 4
		ECHO = 18
		GPIO.setup(TRIG, GPIO.OUT)
		GPIO.setup(ECHO, GPIO.IN)
		GPIO.setup(22, GPIO.IN)
		key1=0

		while True:
			GPIO.output(TRIG, True)
			time.sleep(0.0001)
			GPIO.output(TRIG, False)

			while GPIO.input(ECHO) == False:
				start = time.time()
			while GPIO.input(ECHO) == True:
				end = time.time()
			sig_time = end-start
			distance = sig_time / 0.000058
			if int(distance) < 15:
				key1 = key1+1
				time.sleep(1)
				if key1 == 5 and auto <=1:
					#vs = VideoStream(src=0).start()
					GPIO.output(24, GPIO.HIGH)
					time.sleep(2)
					frame = vs.read()
					GPIO.output(24, GPIO.LOW)
					frame = frame[0:479, 0:639]
					cv.imwrite(filename='images_temp/saved_img.jpg', img=frame)
					time.sleep(.1)
					print("image captured")
					#GPIO.cleanup()
					orientation()
					break
				
			if int(distance) > 15:
				key1 = 0
				if auto > 1:
					auto = 1

			if GPIO.input(22)== GPIO.HIGH:
				#GPIO.cleanup()
				break
	distance_identify(auto)
	#image_identify()

def orientation():
	rotation_ratio = 72
	angles=5
	myList=[None]*rotation_ratio
	mask1List=[None]*rotation_ratio
	rotate1List=[None]*rotation_ratio
	mask2List=[None]*rotation_ratio
	rotate2List=[None]*rotation_ratio
	blackPixList=[None]*rotation_ratio
	differList=[None]*rotation_ratio
	i=j=k=0

	lower=[(0, 100, 100)]
	upper=[(100, 255, 255)]

	img1 = cv.imread('images_temp/normal_crop_img.jpg')
	img2 = cv.imread('images_temp/saved_img.jpg')

	for mask2angle in np.arange(0, 360, angles):
		rotate2List[int(j)]= imutils.rotate(img2, mask2angle)
		edged2 = cv.Canny(rotate2List[j], 0, 200)
		pts2 = np.argwhere(edged2>0)
		y12, x12 = pts2.min(axis=0)
		y22, x22 = pts2.max(axis=0)
		mask2List[int(j)]= y22
		j=j+1

	for mask1angle in np.arange(0, 360, angles):
		rotate1List[int(k)]= imutils.rotate(img1, mask1angle)
		edged1 = cv.Canny(rotate1List[k], 0, 200)
		pts1 = np.argwhere(edged1>0)
		y11, x11 = pts1.min(axis=0)
		y21, x21 = pts1.max(axis=0)
		mask1List[int(k)]= y21
		k=k+1

	edged1 = cv.Canny(rotate1List[mask1List.index(min(mask1List))], 0, 200)
	edged2 = cv.Canny(rotate2List[mask2List.index(min(mask2List))], 0, 200) #150 550 # 0 200
	pts1 = np.argwhere(edged1>0)
	pts2 = np.argwhere(edged2>0)
	y11, x11 = pts1.min(axis=0)
	y12, x12 = pts2.min(axis=0)
	y21, x21 = pts1.max(axis=0)
	y22, x22 = pts2.max(axis=0)
	croppedimg1 = rotate1List[mask1List.index(min(mask1List))][y11:y21, x11:x21]
	croppedimg2 = rotate2List[mask2List.index(min(mask2List))][y12:y22, x12:x22]

	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")

	mask1 = cv.inRange(croppedimg1, lower, upper)
	mask2 = cv.inRange(croppedimg2, lower, upper)

	img_shape1 = croppedimg1.shape
	img_shape2 = croppedimg2.shape

	if img_shape1 == img_shape2:
		crop_mask1 = mask1
		crop_mask2 = mask2
	if img_shape1[0]> img_shape2[0]:
		if img_shape1[1]>=img_shape2[1]:
			crop_mask1 = mask1[0:img_shape2[0], 0:img_shape2[1]]
			crop_mask2 = mask2[0:img_shape2[0], 0:img_shape2[1]]
		if img_shape1[1]<img_shape2[1]:
			crop_mask1 = mask1[0:img_shape2[0], 0:img_shape1[1]]
			crop_mask2 = mask2[0:img_shape2[0], 0:img_shape1[1]]
	elif img_shape1[0]< img_shape2[0]:
		if img_shape1[1]>=img_shape2[1]:
			crop_mask1 = mask1[0:img_shape1[0], 0:img_shape2[1]]
			crop_mask2 = mask2[0:img_shape1[0], 0:img_shape2[1]]
		if img_shape1[1]<img_shape2[1]:
			crop_mask1 = mask1[0:img_shape1[0], 0:img_shape1[1]]
			crop_mask2 = mask2[0:img_shape1[0], 0:img_shape1[1]]


	for angle in np.arange(0, 360, angles):
		myList[int(i)]= imutils.rotate(crop_mask2, angle)
		i=i+1


	for a in range(len(myList)):
		differList[a] = cv.subtract(crop_mask1, myList[a])	

	for b in range(len(myList)):
		blackPixList[b]=np.sum(differList[b]==0)

	orientationValue = ((((mask2List.index(min(mask2List)))*angles)+((blackPixList.index(max(blackPixList)))*angles))-360)-((mask1List.index(min(mask1List)))*angles)
	if orientationValue <= (-360):
		orientationValue = orientationValue + 360
	if orientationValue >= 360:
		orientationValue = orientationValue - 360
	print("max ", max(blackPixList), "index ", blackPixList.index(max(blackPixList)))
	print("orientation :", orientationValue)
	cv.imwrite('images_temp/mask1.jpg', crop_mask1)
	cv.imwrite('images_temp/mask2.jpg', crop_mask2)
	cv.imwrite('images_temp/mask_final.jpg', myList[blackPixList.index(max(blackPixList))])
	
vs = VideoStream(src=0).start()
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
main()
