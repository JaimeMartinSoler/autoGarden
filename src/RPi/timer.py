
# ----------------------------------------------------------------------
# --- timer.py                                                       ---
# ----------------------------------------------------------------------
# --- Contains a class that eases the management of timers           ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-11-17                                             ---
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# IMPORTS
import time
import sqlite3
from jdcal import gcal2jd, jd2gcal




# ----------------------------------------------------------------------
# FUNCTIONS - STATIC
	
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


# nowMillis()
# returns current milliseconds since epoch
def nowMillis():
	return int(round(time.time()*1000))



	
# ----------------------------------------------------------------------
# CLASS TIMER
class Timer:

    # ----------------------------------------------------------------------
    # PARAMETERS
	
	# milliseconds timer
	lastMillis = 0
	periodMillis = 0
	# minutes timer
	lastJulian = 0.0
	periodJulian = 0.0
	periodMins = 0.0
	
	
	
	
    # ----------------------------------------------------------------------
    # CONSTRUCTOR
	def __init__(self, periodMillis=-1, periodMins=-1.0, startReady=True, queryLastMins="", DBcurs=None, DBfield=1, toJulian=True):
	
		# set periods
		self.periodMillis = periodMillis
		self.periodMins = periodMins
		self.periodJulian = periodMins/1440.0
		
		# milliseconds timer
		if (self.isMillisTimer()):
			self.lastJulian = -1.0
			if (startReady):
				self.lastMillis = nowMillis() - self.periodMillis
			else:
				self.lastMillis = nowMillis()
				
		# minutes timer
		elif (self.isMinutesTimer()):
			self.lastMillis = -1
			if (startReady):
				self.lastJulian = nowJulian() - self.periodJulian
			else:
				self.lastJulian = nowJulian()
			if ((len(queryLastMins) > 1) and (DBcurs != None) and (DBfield>=0)):
				DBcurs.execute(queryLastMins)
				DBrow = DBcurs.fetchone()
				if ((len(DBrow)-1) >= DBfield):
					if (toJulian):
						self.lastJulian = datetimeToJulian(DBrow[DBfield])
					else:
						self.lastJulian = DBrow[DBfield]
		
		
		
		
    # ----------------------------------------------------------------------
    # FUNCTIONS
	
	# isMillisTimer(self)
	def isMillisTimer(self):
		return (self.periodMillis >= 0)
		
		
	# isMinutesTimer(self)
	def isMinutesTimer(self):
		return (self.periodMins >= 0.0)
	
	
	# isMinutesTimer(self)
	def setPeriod(self, period):
		# milliseconds timer
		if (self.isMillisTimer()):
			self.periodMillis = period
		# minutes timer
		elif (self.isMinutesTimer()):
			self.periodMins = period
			self.periodJulian = period/1440.0
	
	
	# isReady(self)
	# return True if since the last execution of isReady, time passed > period. Resets currentMillis/Minutes
	def isReady(self):
		# milliseconds timer
		if (self.isMillisTimer()):
			currentMillis = nowMillis()
			if ((currentMillis - self.lastMillis) >= self.periodMillis):
				self.lastMillis = currentMillis
				return True
		# minutes timer
		elif (self.isMinutesTimer()):
			currentJulian = nowJulian()
			if ((currentJulian - self.lastJulian) >= self.periodJulian):
				self.lastJulian = currentJulian
				return True
		return False
	
