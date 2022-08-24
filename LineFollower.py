import cv2
import numpy as np

#hsvValues = [0,0,117,179,22,219]
hsvValues = [0,0,188,179,33,245]
sensors = 3
threshold = 0.2

width, height = 480, 360 
sensitivity = 3
weights=[-25, -15, 0, 15, 25]
curve = 0
fSpeed = 15
cap = cv2.VideoCapture(0)

def thresholding(img):
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	lower = np.array([hsvValues[0],hsvValues[1],hsvValues[2]])
	upper = np.array([hsvValues[3],hsvValues[4],hsvValues[5]])
	mask = cv2.inRange(hsv,lower,upper)
	return mask

def getSensorOutput(imgThres, sensors):
	imgs = np.hsplit(imgThres, sensors)
	totalPixels = (img.shape[1]//sensors) * img.shape[0]
	senOut = []
	for x,im in enumerate(imgs):
		pixelCount = cv2.countNonZero(im)
		if pixelCount > threshold * totalPixels:
			senOut.append(1)
		else:
			senOut.append(0)
		cv2.imshow(str(x), im)
	print(senOut)
	return senOut


def sendCommands(senOut,cx):
	global curve

	#TRANSLATION
	lr = (cx - width//2)//sensitivity
	lr = int(np.clip(lr, -10, 10))

	if lr < 2 and lr > -2:
		lr=0

	#ROTATION
	if senOut == [1,0,0]: curve = weights[0]
	elif senOut == [1, 1, 0]: curve = weights[1]
	elif senOut == [0, 1, 0]: curve = weights[2]
	elif senOut == [0, 1, 1]: curve = weights[3]
	elif senOut == [0, 0, 1]: curve = weights[4]

	elif senOut == [0, 0, 0]: curve = weights[2]
	elif senOut == [1, 1, 1]: curve = weights[2]
	elif senOut == [1, 0, 1]: curve = weights[2]
	
	me.send_rc_control(lr, fSpeed, 0, curve)


def getContours(imgThres,img):
	contours, hierarchy = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	cx = 0
	if len(contours) != 0:
		biggest = max(contours, key = cv2.contourArea)
		x, y, w, h = cv2.boundingRect(biggest)
		cx = x + w // 2
		cy = y + h // 2
		#cv2.drawContours(img, contours, -1, (255,0,255), 7)
		cv2.drawContours(img, biggest, -1, (255,0,255), 7)
		cv2.circle(img, (cx,cy), 10, (0, 255, 0), cv2.FILLED)
	
	return cx

while True:
	_, img = cap.read()
	img = cv2.resize(img, (width, height))
	#img = cv2.flip(img,0)
	
	imgThres = thresholding(img)
	
	cx = getContours(imgThres,img)
	senOut = getSensorOutput(imgThres, sensors)
	sendCommands(senOut,cx)
	cv2.imshow("Output", img)
	cv2.imshow("Path", imgThres)
	cv2.waitKey(1)