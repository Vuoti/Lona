#****************************************************************************
# This script generates a printout with the active Ngrok url as a qr-code and
# prints it on a serial connected thermal printer.
# An additional bashscript (../getNgrokUrl.sh) is used to get the Ngrok url.
# If Ngrok is not used you can pass another url as an argument when running
# the script, e.g. python printer/urlPrintoutGenerator -url "localhost:3000"
# ! Always run the script from the toplevel folder
#
# Written by Andre Fritzinger
#
#****************************************************************************
# Required Libraries:
# pip2.7 install pillow qrcode[pil]

from Adafruit_Thermal import * # used for printing on the thermal printer
from PIL import Image, ImageDraw, ImageFont # used for dynamic image generation
import qrcode # used for the qr-code generation
import os.path, argparse, subprocess

printer = Adafruit_Thermal('/dev/serial0', 9600, timeout=5)
qr = qrcode.QRCode(
    version = 1,
    error_correction = qrcode.constants.ERROR_CORRECT_H,
    box_size = 6,
    border = 4,
)

# Get the ngrok url
process = subprocess.Popen(['sh', 'ngrok/getNgrokUrl.sh'], stdout=subprocess.PIPE)
output, err = process.communicate()
url = 'https://' + output

# or use the url from a passed commandline argument
ap = argparse.ArgumentParser()
ap.add_argument('-url', '--url', required=False,
	help='url to ngrok.io')
if(ap.parse_args().url is not None):
    url = ap.parse_args().url

print ('URL: ' + url)

# Create the canvas
image = Image.new('RGB', (384,986))
draw = ImageDraw.Draw(image)

# Use the urlPrintout template image
template = Image.open('printer/template/template-urlPrintout.jpg')
image.paste(template, (0,0))

# Generate the QR code
qr.add_data(url)
qr.make(fit=True)
qrImg = qr.make_image()
image.paste(qrImg, (65,580))

# Add the url
(x, y) = (50, 830)
color = 'rgb(0, 0, 0)'
font = ImageFont.truetype('printer/fonts/Bitter-Italic.ttf', size=29)
w, h = draw.textsize(url, font=font)
draw.text(((384-w)/2, y), url, fill=color, font=font)

# Rotate the image by 180deg, save and print it
image.rotate(180).save('printer/urlPrintout.jpg')
printer.upsideDownOn()
printer.justify('C')
printer.printImage(Image.open('printer/urlPrintout.jpg'), True)
printer.feed(4)
