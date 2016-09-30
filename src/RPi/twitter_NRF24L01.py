#!/usr/bin/python


    ## ----------------------------------------------------------------------
    ## --- twitter_NRF24L01.py                                            ---
    ## ----------------------------------------------------------------------
    ## --- autoGarden main RPi file, to manage sensors and Arduino comm.  ---
    ## --- Arduino requirements: execute ard_NRF24L01_LM35.ino            ---
    ## --- RPi comm.: NRF24L01 2.4GHz wireless transciever                ---
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
from twython import Twython, TwythonError
# import keys and tokens (file 'twitterPass.py' is ignored in .gitignore by GitHub)
from twitterPass import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO, probably because you need 'sudo' privileges")
	


	
# -------------------------------------------------------------------
# TWITTER

# -------------------
# Function tweetMsg
# 	it makes a new tweet from the twitter object and the text to tweet
#   return: True(tweeted), False(error)
def tweetMesg(t,txt):
	try:
		t.update_status(status=txt)
		return True
	except TwythonError as e:
		print (e)
		return False
	
# get twitter instance from keys and tokens
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)


	
	
# -------------------------------------------------------------------
# GPIO

# -------------------
# Function callback_tweet(1 argument is mandatory)
#	callback function that makes a message and tweets it
def callback_tweet(pin):
	print ("\npin " + str(pin) + " rising edge detected: tweet")
	tweetText = "Termpeture is over 30 celsius!!! [" + time.strftime("%Y-%m-%d %H:%M:%S") + "]"
	if tweetMesg(t=twitter,txt=tweetText):
		print ("tweeted successfully:\n" + tweetText)

# Twitter pin mode and setup (pull-down resistor: LOW stable value as default)
pin_arduino = 37
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(pin_arduino, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.add_event_detect(pin_arduino, GPIO.RISING, callback=callback_tweet, bouncetime=50)

# Finish pin mode and setup (pull-down resistor: LOW stable value as default)
pin_finish = 35
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(pin_finish, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# wait until pin_finish is rised, to keep alive the callback 
GPIO.wait_for_edge(pin_finish, GPIO.RISING)
print("\npin " + str(pin_finish) + " rising edge detected: finish")

# clear the configuration
GPIO.cleanup()
