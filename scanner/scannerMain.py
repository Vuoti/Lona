#****************************************************************************
# This script waits for a frame to be inserted into the Lona phone, plays a
# soundFx and runs the barcode scanner script
# (scanner/barcodeScannerVideoStream.py) accordingly.
# ! Always run this script from the toplevel folder
#
# Written by Andre Fritzinger
#
#****************************************************************************
# To-Do:
# - Fix the Neopixel-Audio PWM conflict
# - Add microphone and buttons to record a message or start a call

from __future__ import print_function
import RPi.GPIO as GPIO
import os, subprocess

buttonPin = 23
GPIO.setmode(GPIO.BCM) # Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Enable button with pull-up
GPIO.setwarnings(False)
FNULL = open(os.devnull, 'w') # Redirect the terminal output because omxplayer has no --silent mode

print("Waiting for Frame to be inserted")

# Called when the button is tapped. Plays the "insert" soundFx and runs the barcode scanning script
def tap():
  print ("\nFrame inserted")
  #subprocess.Popen(['sudo', 'python', 'ledOn.py']) # PMW conflict with audio, LED is currently not supported
  subprocess.Popen(['omxplayer', '-o', 'local', 'scanner/soundFx/insert.mp3'], stdout=FNULL, stderr=subprocess.STDOUT)
  subprocess.call(['sudo', 'python3', 'scanner/barcodeScannerVideoStream.py'])

# Main loop
while(True):
    button_state = GPIO.input(buttonPin)
    if button_state == False:
        tap()
