# ----------------------------------------------------------------------
# --- global.cpp                                                     ---
# ----------------------------------------------------------------------
# --- Global variables     										     ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-10-25                                             ---
# ----------------------------------------------------------------------




# ----------------------------------------------------------------------
# IMPORTS
from action import Action
import sqlite3
import time
from jdcal import gcal2jd, jd2gcal




# ----------------------------------------------------------------------
# PARAMETERS

# Actions
rxAction = Action()			# Action for RX general propose
rxNormalAction = Action()	# Action for RX Normal actions, answers to requests from RPi DB,timers checking module
rxTwitterAction = Action()	# Action for RX Twitter actions, answers to requests from RPi Twitter checking module
rxArduinoAction = Action()	# Action for RX Arduino actions, urgents messages sent by Arduino
txNormalAction = Action()	# Action for TX Normal actions, requests from RPi DB,timers checking module
txTwitterAction = Action()	# Action for TX Twitter actions, requests from RPi Twitter checking module

#  DB parameteres
DB_PATH = 'db'
DB_NAME = 'autoGarden.db'
DB_FULL_PATH = DB_PATH + '/' + DB_NAME
DB_CONN = sqlite3.connect(DB_FULL_PATH)
DB_CONN_N = 0




# ----------------------------------------------------------------------
# FUNCTIONS

# datetimeToJulian(datetime)
# converts datetime in string format (i.e. "2016-11-09 23:01:26" or "2016-11-09") in julian day number
def datetimeToJulian(datetime):
	datetime_len = len(datetime)
	if (datetime_len<10):
		return 0.0
	year  = int(datetime[0:4])
	month = int(datetime[5:7])
	day   = int(datetime[8:10])
	jdArray = gcal2jd(year,month,day)
	jd = jdArray[0] + jdArray[1]
	if (datetime_len >= 19):
		hour  = int(datetime[11:13])
		min   = int(datetime[14:16])
		sec   = int(datetime[17:19])
		jd += (hour/24.0) + (min/1440.0) + (sec/86400.0)
	return jd

	
# nowDatetime()
# now date and time in standard format (i.e. "2016-11-09 23:01:26")
def nowDatetime():
	return time.strftime('%Y-%m-%d %H:%M:%S')
	
# nowJulian()
# now julian date time
def nowJulian():
	return datetimeToJulian(nowDatetime())

