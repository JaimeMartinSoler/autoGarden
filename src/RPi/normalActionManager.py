
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
from timer import *




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
	
	# parameters: timers queries
	query_TEMP_LM35 = 'SELECT * FROM WEATHER WHERE WPAR=\'{}\' AND WPARID=\'{}\' ORDER BY DATETIME DESC LIMIT 1;'.format(WPAR_TEMP_L, WPARID_TEMP_LM35_L)
	query_TEMP_DHT  = 'SELECT * FROM WEATHER WHERE WPAR=\'{}\' AND WPARID=\'{}\' ORDER BY DATETIME DESC LIMIT 1;'.format(WPAR_TEMP_L, WPARID_TEMP_DHT_L)
	query_HUMI_DHT  = 'SELECT * FROM WEATHER WHERE WPAR=\'{}\' AND WPARID=\'{}\' ORDER BY DATETIME DESC LIMIT 1;'.format(WPAR_HUMI_L, WPARID_HUMI_DHT_L)
	query_RAIN_MH   = 'SELECT * FROM WEATHER WHERE WPAR=\'{}\' AND WPARID=\'{}\' ORDER BY DATETIME DESC LIMIT 1;'.format(WPAR_RAIN_L, WPARID_RAIN_MH_L)
	# parameters: timers
	timer_TEMP_LM35 = Timer(periodMins=30.0, queryLastMins=query_TEMP_LM35, DBcurs=DBcursor, DBfield=1, toJulian=True)
	timer_TEMP_DHT = Timer(periodMins=5.0, queryLastMins=query_TEMP_DHT, DBcurs=DBcursor, DBfield=1, toJulian=True)
	timer_HUMI_DHT = Timer(periodMins=5.0, queryLastMins=query_HUMI_DHT, DBcurs=DBcursor, DBfield=1, toJulian=True)
	timer_RAIN_MH = Timer(periodMins=5.0, queryLastMins=query_RAIN_MH, DBcurs=DBcursor, DBfield=1, toJulian=True)

	# setup: create initial tx and rx
	txNormalAction.set()
	rxNormalAction.set()
	txNormalAction.setId(intToId(ACTION_NORMAL_ID - ACTION_TYPES_GLOBAL*2))	# ready for autoincrement
	
	# variables for txNormalAction text
	txTextDef = "XXX,"+BOARD_ID+","+BOARD_A0_ID+","+TYPE_NORMAL_S+",{},{},{}"
	txText = txTextDef
	txTimerIsReady = False
	
	# loop: check timers and DB, updating txNormalAction if so
	while (STATUS.get("isAlive")):
	
		# delay
		time.sleep(1.0)
		
		# check timers
		if (timer_TEMP_LM35.isReady()):
			txText = txTextDef.format(FUNC_GET_S, WPAR_TEMP_L, WPARID_TEMP_LM35_L)
			txTimerIsReady = True
		elif (timer_TEMP_DHT.isReady()):
			txText = txTextDef.format(FUNC_GET_S, WPAR_TEMP_L, WPARID_TEMP_DHT_L)
			txTimerIsReady = True
		elif (timer_HUMI_DHT.isReady()):
			txText = txTextDef.format(FUNC_GET_S, WPAR_HUMI_L, WPARID_HUMI_DHT_L)
			txTimerIsReady = True
		elif (timer_RAIN_MH.isReady()):
			RAIN_MH_time = 1500
			RAIN_MH_period = 50
			txText = txTextDef.format(FUNC_GET_S, WPAR_RAIN_L, WPARID_RAIN_MH_L) + ",{},{}".format(RAIN_MH_time,RAIN_MH_period)
			txTimerIsReady = True

		# if any timer is ready, set tx actions
		if (txTimerIsReady):
			txTimerIsReady = False
		
			# set tx action and wait rx action
			try:
				setTXwaitRX(txNormalAction, rxNormalAction, txText, timeOut=5000, autoIncrement=True, checkRXid=True)
			# if (not STATUS.get("isAlive"))
			except RuntimeError:		
				return
			# if (Timeout)
			except OSError as te:		
				LOG(LOG_ERR,"<<< WARNING: TwitterAction TimeoutError: \"{}\" >>>".format(te), logPreLn=True)
				continue
			# if (rx.ID is not as expected)
			except ValueError as ve:	
				LOG(LOG_ERR,"<<< WARNING: rxTwitterAction ValueError: \"{}\" >>>".format(ve), logPreLn=True)
				continue


	