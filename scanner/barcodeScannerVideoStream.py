#****************************************************************************
# This script enables the PiCamera, starts a video stream and looks for
# barcodes within the video frames. In case of detection, the barcode data
# gets decoded and if possible the corresponding soundfile/voice message
# played back.
# ! Always run this script from the toplevel folder
#
# Written by Andre Fritzinger
#
#****************************************************************************
# To-Do:
# - Fix the Neopixel-Audio PWM conflict
# - Move all audio playback to scannerMain.py > Just read barcode and return the data
from imutils.video import VideoStream # Used to get the PiCamera video stream
from pyzbar import pyzbar # Barcode recognition library
from datetime import date
from os import walk
import os, subprocess, imutils, time

today = str(date.today())[2:4] + str(date.today())[5:7] + str(date.today())[8:10]
startTime = time.time()
intervallTimeScan = 15.0
barcodeDetected = False
FNULL = open(os.devnull, 'w') # Redirect the terminal output because omxplayer has no --silent mode

print("[Starting] Barcode scanner")
#subprocess.call(["sudo", "python", "ledOn.py"]) # PMW conflict with audio, LED is currently not supported

# Initialize the video stream and allow the camera sensor to warm up
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# Loop over the frames from the video stream and look for barcodes
while not barcodeDetected:

	# grab the frame from the threaded video stream and resize it
	frame = vs.read()
	frame = imutils.resize(frame, width=400)

	# find barcodes in the frame and decode them
	barcodes = pyzbar.decode(frame)
	for barcode in barcodes:
		barcodeDetected = True # Found a barcode, so we can stop scanning
		barcodeData = barcode.data.decode("utf-8") # the barcode data is a bytes object, so we need to convert it to a string
		print("Barcode detected: " + barcodeData)

		for root, directories, filenames in os.walk('public/uploads/'):
			for filename in filenames:
				if(filename == barcodeData + '.wav'):
					#subprocess.call(["sudo", "python", "ledGreen.py"]) # # PMW conflict with audio, LED is currently not supported
					print("Playing back the audio file: " + root + '/' + barcodeData + '.wav')
					subprocess.call(['omxplayer', '-o', 'local', 'scanner/soundFx/success.mp3'], stdout=FNULL, stderr=subprocess.STDOUT)
					subprocess.Popen(["omxplayer", "-o", "local", root + '/' + barcodeData + ".wav"], stdout=FNULL, stderr=subprocess.STDOUT)
					break

	# Quit scanning after 15 seconds
	if time.time() - startTime > intervallTimeScan:
		#subprocess.call(["sudo", "python", "ledRed.py"]) # PMW conflict with audio, LED is currently not supported
		subprocess.call(['omxplayer', '-o', 'local', 'scanner/soundFx/fail.mp3'], stdout=FNULL, stderr=subprocess.STDOUT)
		print("Could not detect any barcodes")
		break

print("[Stopped] Barcode scanner")
vs.stop()
#subprocess.call(["sudo", "python", "ledOff.py"]) # PMW conflict with audio, LED is currently not supported
