
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
	query_DATETIME = 'SELECT DATETIME FROM WEATHER WHERE WPAR=\'{}\' AND WPARID=\'{}\' AND TYPE=\'{}\' ORDER BY DATETIME DESC LIMIT 1;'
	query_TEMP_LM35 = query_DATETIME.format(WPAR_TEMP_L, WPARID_TEMP_LM35_L, TYPE_NORMAL_L)
	query_TEMP_DHT  = query_DATETIME.format(WPAR_TEMP_L, WPARID_TEMP_DHT_L, TYPE_NORMAL_L)
	query_HUMI_DHT  = query_DATETIME.format(WPAR_HUMI_L, WPARID_HUMI_DHT_L, TYPE_NORMAL_L)
	query_RAIN_MH   = query_DATETIME.format(WPAR_RAIN_L, WPARID_RAIN_MH_L, TYPE_NORMAL_L)
	# parameters: timers
	timer_TEMP_LM35 = Timer(periodMins=30.0, queryLastMins=query_TEMP_LM35, DBcurs=DBcursor, toJulian=True)
	timer_TEMP_DHT = Timer(periodMins=5.0, queryLastMins=query_TEMP_DHT, DBcurs=DBcursor, toJulian=True)
	timer_HUMI_DHT = Timer(periodMins=5.0, queryLastMins=query_HUMI_DHT, DBcurs=DBcursor, toJulian=True)
	timer_RAIN_MH = Timer(periodMins=5.0, queryLastMins=query_RAIN_MH, DBcurs=DBcursor, toJulian=True)

	# setup: create initial tx and rx
	txNormalAction.set()
	rxNormalAction.set()
	txNormalAction.setId(intToId(ACTION_NORMAL_ID - ACTION_TYPES_GLOBAL*2))	# ready for autoincrement
	
	# other parameters
	RAIN_MH_time = 1500
	RAIN_MH_period = 50
	RAIN_MH_append = ',{},{}'.format(RAIN_MH_time, RAIN_MH_period)
	
	# loop: check timers and DB, updating txNormalAction (getToDB) if so
	while (STATUS.get("isAlive")):
	
		# delay
		time.sleep(1.0)
		
		# check timers
		if (timer_TEMP_LM35.isReady()):
			getToDB(WPAR_TEMP_L, WPARID_TEMP_LM35_L, type=TYPE_NORMAL_L)
		elif (timer_TEMP_DHT.isReady()):
			getToDB(WPAR_TEMP_L, WPARID_TEMP_DHT_L, type=TYPE_NORMAL_L)
		elif (timer_HUMI_DHT.isReady()):
			getToDB(WPAR_HUMI_L, WPARID_HUMI_DHT_L, type=TYPE_NORMAL_L)
		elif (timer_RAIN_MH.isReady()):
			getToDB(WPAR_RAIN_L, WPARID_RAIN_MH_L, type=TYPE_NORMAL_L, append=RAIN_MH_append)


	