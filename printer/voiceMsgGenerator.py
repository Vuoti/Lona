#****************************************************************************
# This script generates a printout with details to a recieved voice-message,
# creates a corresponding barcode and prints it on a serial connected
# thermal printer.
# You have to pass the barcode data, date, voice message length, and name of
# the creator, when running this scriptself.
# e.g. python printer/voiceMsgGenerator.py -b '151023' -d '07.03.19 | 15:10' -l '4:20' -n 'Mary Jane'
# ! Always run the script from the toplevel folder
#
# Written by Andre Fritzinger
#
#****************************************************************************
# Required libraries:
# pip2.7 install pillow

from Adafruit_Thermal import * # used for printing and barcode generation
from PIL import Image, ImageDraw, ImageFont # used for dynamic image generation
import os.path, argparse

printer = Adafruit_Thermal('/dev/serial0', 9600, timeout=5)

# Get the passed commandline arguments
ap = argparse.ArgumentParser()
ap.add_argument('-b', '--barcode', required=True,
	help='Input data for the barcode')
ap.add_argument('-d', '--date', required=True,
	help='Date and Time')
ap.add_argument('-l', '--length', required=True,
	help='Length of the message')
ap.add_argument('-n', '--name', required=True,
	help='Name of the recording person')

barcode = ap.parse_args().barcode
date = ap.parse_args().date
length = ap.parse_args().length
name = ap.parse_args().name.decode('utf-8')
filePath = 'public/uploads/' + date[6:8] + date[3:5] + date[0:2] + '/' + barcode + '.jpg'

# Easter eggs
if(name == 'Nyancat'):
	barcode = 'NYANCAT'
elif(name == 'Geburtstag'):
	barcode = 'BDAYOPA'

# Create the Canvas
image = Image.new('RGB', (384,446))
draw = ImageDraw.Draw(image)

# Look for an existing profile picture of the voicemsg creator or use a default picture instead
if(os.path.isfile('printer/profile-pictures/' + name + '.jpg')):
	print('Using the picture of ' + name)
	profilePic = Image.open('printer/profile-pictures/' + name + '.jpg')
else:
	print('No profile picture yet, generating default picture')
	profilePic = Image.open('printer/initials-assets/' + name[0].upper() + ' .jpg')

image.paste(profilePic, (90,25))

# Use the voicemsg template image
template = Image.open('printer/template/template_voicemsg.png')
image.paste(template, (0,0), mask=template)

# Add the name of the voicemsg creator to the canvas, e.g. name = 'Mary Jane'
(x, y) = (50, 385)
color = 'rgb(0, 0, 0)'
font = ImageFont.truetype('printer/fonts/Bitter-Bold.ttf', size=36)
w, h = draw.textsize(name, font=font)
draw.text(((384-w)/2, y), name, fill=color, font=font)

# Add the voicemsg length to the canvas, e.g. length = '4:20s'
(x, y) = (115, 265)
w, h = draw.textsize(length, font=font)
draw.text((x, y), length, fill=color, font=font)

# Add the date and time to the canvas, e.g. date = '07.03.19 | 15:10'
(x, y) = (115, 230)
font = ImageFont.truetype('printer/fonts/Bitter-Italic.ttf', size=30)
w, h = draw.textsize(date, font=font)
draw.text((x, y), date, fill=color, font=font)

# Rotate the image by 180deg and save it next to the voicemsg file
image.rotate(180).save(filePath)

# Print the Barcode, e.g. barcode = '151023'
printer.upsideDownOn()
printer.justify('C')
printer.setBarcodeHeight(100)
printer.printBarcode(barcode, printer.CODE128)
printer.feed(3)

# Load the generated image and print it
printer.printImage(Image.open(filePath), True)
printer.feed(6)
