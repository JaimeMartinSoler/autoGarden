
# ----------------------------------------------------------------------
# --- normalActionManager.py                                         ---
# ----------------------------------------------------------------------
# --- This file is meant to manager the txNormalAction object,       ---
# --- checking timers and database to request more info to Arduino   ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-11-10                                             ---
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# IMPORTS
import time
import sqlite3
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
from action import *
from glob import *
from DBmanager import *
from actionManager import *




# ----------------------------------------------------------------------
# FUNCTIONS

# -------------------------------------
# txNormalActionManager()
# Checks the status of the sensors and autonomously generates and Action, if needed
# This function is meant to be executed in the RX wait loop every few milliseconds
# return: true(action generated), false(no action generated)
def txNormalActionManager():

	# wait for rx setup
	time.sleep(1.000)
	
	# parameters: DBconn, DBcursor
	DBconn = sqlite3.connect(DB_FILE_NAME_FULL)
	DBcursor = DBconn.cursor()
	# parameters: timers
	TEMP_AIR_period = 5.0							# TEMP_AIR_period in minutes
	TEMP_AIR_period_j = TEMP_AIR_period/(1440.0)	# TEMP_AIR_period in julian
	TEMP_AIR_last_j = 0.0
	
	# setup: time parameters
	DBcursor.execute('SELECT * FROM WEATHER WHERE WPAR=\'TEMP\' AND WPARID=\'AIR\' ORDER BY DATETIME DESC LIMIT 1;')
	DBrow = DBcursor.fetchone()
	if (DBrow is not None):
		TEMP_AIR_last_j = datetimeToJulian(DBrow[1])
	# setup: id counters
	countId = 0
	# setup: create initial tx and rx
	txNormalAction.set()
	rxNormalAction.set()
	txNormalAction.setId(intToId(ACTION_NORMAL_ID - ACTION_TYPES_GLOBAL*2))	# ready for autoincrement
	
	# loop: check timers and DB, updating txNormalAction if so
	while (PROCESS.isAlive):
	
		# delay
		time.sleep(1.0)
		
		# update nowJulianDT
		nowJulianDT = nowJulian()
		
		# TEMP_AIR management
		if ((nowJulianDT - TEMP_AIR_last_j) >= TEMP_AIR_period_j):
			TEMP_AIR_last_j = nowJulianDT
			
			# set tx action and wait rx action
			try:
				setTXwaitRX(txNormalAction, rxNormalAction, "XXX,R0,A0,NR,GET,TEMP,AIR", timeOut=5000, autoIncrement=True, checkRXid=True)
			except RuntimeError:	# if (not PROCESS.isAlive)
				return
			except OSError as te:	# if (Timeout)
				LOG(LOG_ERR,"<<< WARNING: TwitterAction TimeoutError: \"{}\" >>>".format(te), logPreLn=True)
				continue
			except ValueError as ve:	# if (rx.ID is not as expected)
				LOG(LOG_ERR,"<<< WARNING: rxTwitterAction ValueError: \"{}\" >>>".format(ve), logPreLn=True)
				continue
				
		

	