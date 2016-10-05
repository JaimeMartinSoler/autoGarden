#!/usr/bin/python


    ## ----------------------------------------------------------------------
    ## --- twitter_GPIO.py                                                ---
    ## ----------------------------------------------------------------------
    ## --- autoGarden main RPi file, to manage sensors and Arduino comm.  ---
    ## --- Arduino requirements: execute ard_GPIO_LM35.ino                ---
    ## --- RPi comm.: GPIO (input 100ms pulse through pin 37)             ---
    ## ----------------------------------------------------------------------
    ## --- Author: Jaime Martin Soler                                     ---
    ## --- Date  : 30/09/2016                                             ---
    ## ----------------------------------------------------------------------


# Twython reference:
# https://twython.readthedocs.io/en/latest/index.html
#
# GPIO reference:
# https://sourceforge.net/p/raspberry-gpio-python/wiki/Examples/
#
# Raspberry Pi 3 pins:
# http://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Layout-Model-B-Plus-rotated-2700x900-1024x341.png


# -------------------------------------------------------------------
# IMPORTS

import time
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO, probably because you need 'sudo' privileges")
	


# -------------------------------------------------------------------
# GPIO

# Set GPIO pins
GPIO.setmode(GPIO.BOARD) 
pins = [3,5,7,8,10,11,12,13,15,16,18,19,21,22,23,24,26,29,31,32,33,35,36,37,38,40]
for p in pins:
    GPIO.setup(p, GPIO.OUT)

# Toggle pins
while True:
	for p in pins:
		GPIO.output(p, GPIO.LOW)
	time.sleep(0.500)
	for p in pins:
		GPIO.output(p, GPIO.HIGH)
	time.sleep(0.500)
		
# clear the configuration
GPIO.cleanup()

