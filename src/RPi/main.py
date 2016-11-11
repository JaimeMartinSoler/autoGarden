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
import time
import signal
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
import threading
import signal
from glob import *
from rxtx import *
from normalActionManager import *
from DBmanager import *




# --------------------------------------------------------------
# MAIN LOOP

def main():

	# create threads
	thread_rx = threading.Thread(target=rx)
	thread_txNormalActionManager = threading.Thread(target=txNormalActionManager)
	# start threads
	thread_rx.start()
	thread_txNormalActionManager.start()

	# wait loop
	try:
		while(True):
			time.sleep(1.0)
	# close threads and DB if KeyboardInterrupt
	except KeyboardInterrupt:
		LOG(LOG_ERR, "KeyboardInterrupt: Closing threads and DB", logPreLn=True)
		# set PROCESS.isAlive = False
		PROCESS.isAlive = False
		# join (wait) threads
		thread_rx.join()
		thread_txNormalActionManager.join()
		# close DB
		DBclose()
		LOG(LOG_ERR, "KeyboardInterrupt: Threads and DB successfully closed")

		
# --------------------------------------------------------------
# MAIN CALL
main()
