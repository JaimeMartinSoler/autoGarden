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
from glob import *
import time
import signal
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
import threading
import signal
from rxtx import *
from normalActionManager import *
from twitterActionManager import *
from DBmanager import *
from actionManager import *




# --------------------------------------------------------------
# MAIN LOOP
def main():

	# mainExit control parameter
	mainExit = False
	
	# create threads
	thread_rx = threading.Thread(target=rx)
	thread_txNormalActionManager = threading.Thread(target=txNormalActionManager)
	thread_txTwitterActionManager = threading.Thread(target=txTwitterActionManager)
	# start threads
	thread_rx.start()
	thread_txNormalActionManager.start()
	thread_txTwitterActionManager.start()

	# wait loop
	try:
		while(STATUS.get("isAlive")):
			time.sleep(1.0)
		mainExit = True
	# close threads and DB if KeyboardInterrupt
	except KeyboardInterrupt:
		mainExit = True
	
	if (mainExit):
		LOG(LOG_ERR, "mainExit: closing threads, closing DB, restoring status...", logPreLn=True)
		# STATUS.set("isAlive", False)
		STATUS.set("isAlive", False)
		# join (wait) threads
		thread_rx.join()
		thread_txNormalActionManager.join()
		thread_txTwitterActionManager.join()
		# close DB
		DBclose()
		# restore status to default
		STATUS.fileToDefault()
		LOG(LOG_ERR, "mainExit: Threads and DB successfully closed\n")
	else:
		LOG(LOG_ERR, "<<< ERROR: main end reached but mainExit=false >>>\n", logPreLn=True)
		
# --------------------------------------------------------------
# MAIN CALL
main()
