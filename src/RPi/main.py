#!/usr/bin/python

# ----------------------------------------------------------------------
# --- main.py                                                        ---
# ----------------------------------------------------------------------
# --- Autogarden Arduino main file                                   ---
# --- Arduino-RaspberryPi high level communication of weather params ---
# --- NRF24 config:  http:#invent.module143.com/daskal_tutorial/rpi-3-tutorial-14-wireless-pi-to-arduino-communication-with-nrf24l01/
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-10-23                                             ---
# ----------------------------------------------------------------------




# --------------------------------------------------------------
# IMPORTS
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
from action import Action, idAdd
from rxtx import *
import thread
import signal
from glob import *




# --------------------------------------------------------------
# PARAMETERS

radioMain = NRF24(GPIO, spidev.SpiDev())



# --------------------------------------------------------------
# FUNCTIONS
	
# -------------------------------------
# setup_NRF24(NRF24)
def setup_GPIO():
	# GPIO as BCM mode as per lib_nrf24 requires
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

# -------------------------------------
# signalHandler(signum, frame)
def signalHandler(signum, frame):
	LOG(LOG_ERR, '<<< Program finished by user, closing DB >>>\n', logPreLn=True)
	DB_CONN.close()
	
	
	

# --------------------------------------------------------------
# SETUP
setup_GPIO()
setup_NRF24(radioMain)
setup_DB()
signal.signal(signal.SIGINT, signalHandler)

 
 
# --------------------------------------------------------------
# MAIN LOOP



# manageTxNormalAction LOOP
try:
   thread.start_new_thread(manageTxNormalAction,())
except:
   print "Error: unable to start thread"

# RX LOOP
rx(radioMain, rxLoop=True)

