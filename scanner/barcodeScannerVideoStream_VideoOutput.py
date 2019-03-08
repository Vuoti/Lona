#****************************************************************************
# This script enables the PiCamera, starts a video stream, shows this stream
# in an cv2.window and looks for barcodes within the video frames.
# In case of detection, the barcode gets highlighted and the barcode data
# gets displayed.
#
#****************************************************************************

# import the necessary packages
from imutils.video import VideoStream # Used to get the PiCamera video stream
from pyzbar import pyzbar # Barcode recognition library
import cv2 # Used to show the videostream
import datetime, imutils, time

# initialize the video stream and allow the camera sensor to warm up
print("[Starting] Barcode scanner")

# vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# Loop over the frames from the video stream and look for barcodes
while True:

	# grab the frame from the threaded video stream and resize it
	frame = vs.read()
	frame = imutils.resize(frame, width=400)

	# find barcodes in the frame and decode them
	barcodes = pyzbar.decode(frame)
	for barcode in barcodes:

		# Draw an bounding box surrounding the barcode on the image
		(x, y, w, h) = barcode.rect
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

		# the barcode data is a bytes object, so we need to convert it to a string
		barcodeData = barcode.data.decode("utf-8")
		barcodeType = barcode.type

		# draw the barcode data and barcode type on the image
		text = "{} ({})".format(barcodeData, barcodeType)
		cv2.putText(frame, text, (x, y - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

	# show the output frame
	cv2.imshow("Barcode Scanner", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

print("[Stopped] Barcode scanner")
cv2.destroyAllWindows()
vs.stop()
