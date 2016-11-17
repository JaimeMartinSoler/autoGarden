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





# from timer import *
# import sqlite3
# DBconn = sqlite3.connect(DB_FILE_NAME_FULL)
# DBcursor = DBconn.cursor()
# tmr = Timer(periodMins=0.01, queryLastMins='SELECT * FROM WEATHER WHERE WPAR=\'TEMP\' AND WPARID=\'AIR\' ORDER BY DATETIME DESC LIMIT 1;', DBcurs=DBcursor, DBfield=1, toJulian=True)
# print("   lastMillis = {}".format(tmr.lastMillis))
# print("   periodMillis = {}".format(tmr.periodMillis))
# print("   lastMins = {}".format(tmr.lastMins))
# print("   periodMins = {}".format(tmr.periodMins))

# print("\n   isReady() = {}".format(tmr.isReady()))
# time.sleep(1.000)
# print("\n   isReady() = {}".format(tmr.isReady()))
# exit()


# --------------------------------------------------------------
# MAIN LOOP

def main():

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
		thread_txTwitterActionManager.join()
		# close DB
		DBclose()
		LOG(LOG_ERR, "KeyboardInterrupt: Threads and DB successfully closed")

		
# --------------------------------------------------------------
# MAIN CALL
main()
