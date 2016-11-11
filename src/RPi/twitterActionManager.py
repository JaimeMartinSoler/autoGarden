
# ----------------------------------------------------------------------
# --- twitterActionManager.py                                        ---
# ----------------------------------------------------------------------
# --- This file is meant to manage the txTwitterAction object,       ---
# --- checking timers and database to request more info and tweet    ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-11-11                                             ---
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# IMPORTS
import time
import sqlite3
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
from action import *
from glob import *
from DBmanager import *
from twython import Twython, TwythonError
from twitterPass import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET




# ----------------------------------------------------------------------
# FUNCTIONS

# -------------------------------------
# txTwitterActionManager()
# Checks the DB and twitter and generates and action, if needed.
# This function is meant to be a thread
def txNormalActionManager():

	# wait for rx setup
	time.sleep(1.500)
	
	# parameters: DBconn, DBcursor
	DBconn = sqlite3.connect(DB_FULL_PATH)
	DBcursor = DBconn.cursor()
	# parameters: timers
	TEMP_AIR_period = 30.0							# TEMP_AIR_period in minutes
	TEMP_AIR_period_j = TEMP_AIR_period/(1440.0)	# TEMP_AIR_period in julian
	TEMP_AIR_last_j = 0.0
	# parameters: twitter
	twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	
	# setup: create a fake (txSuccess=1) to avoid tx and jump wait loop
	txTwitterAction.txSuccess = 1
	txTwitterAction.txReadyToTx = True
	
	# loop: check timers and twitter, updating txTwitterAction if so
	while (PROCESS.isAlive):
		
		# wait for previous action to be transmitted
		while(txTwitterAction.txReadyToTx and txTwitterAction.txSuccess<=0):
			# Check PROCESS.isAlive
			if (not PROCESS.isAlive):
				return
			time.sleep(0.100)
		nowJulianDT = nowJulian()
		
		# TEMP_AIR management
		if ((nowJulianDT - TEMP_AIR_last_j) >= TEMP_AIR_period_j):
			# get last TEMP_AIR temperature from DB
			DBcursor.execute('SELECT * FROM WEATHER WHERE WPAR=\'TEMP\' AND WPARID=\'AIR\' ORDER BY DATETIME DESC LIMIT 1;')
			DBrow = DBcursor.fetchone()
			# make a tweet about the TEMP_AIR
			if (DBrow is not None):
			TEMP_AIR_last_j = datetimeToJulian(DBrow[1])
			TEMP_AIR_value = DBrow[6]
			tweetText = "Oh dear, the temperature is {:.1f} celsius, that is so grateful!".format(TEMP_AIR_value)
			try:
				twitter.update_status(status=tweetText)
			except TwythonError as e:
				LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e))
		else:
			LOG(LOG_WAR,"<<< WARNING: No rows found in DB (txTwitterActionManager, WEATHER) >>>")
			
		# delay
		time.sleep(1.0)

