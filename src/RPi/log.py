#!/usr/bin/python

# ----------------------------------------------------------------------
# IMPORTS
import os
import time




# ----------------------------------------------------------------------
# PARAMETERS

# LOG_LEVEL_X
LOG_DEB = 0   # debug
LOG_DET = 1   # detail
LOG_INF = 2   # info
LOG_WAR = 3   # warning
LOG_ERR = 4   # error
LOG_CRS = 5   # crash
LOG_OFF = 6   # off

# LOG_LEVEL
LOG_LVL = LOG_DEB	# the current log level

# LOG_PATHS
LOG_PATH = 'log'
LOG_FILE = 'log_'+time.strftime('%Y%m%d')+'.txt'
LOG_TIME_FORMAT = '[%Y-%m-%d %H:%M:%S]: '




# ----------------------------------------------------------------------
# FUNCTIONS

# -------------------------------------
# LOG
def LOG(logLevel, logText, logPrint=True, logFile=True, logPrintDate=True, logFileDate=True, logPreLn=False):
	if (logLevel >= LOG_LVL):
		preLn = ''
		if (logPreLn):
			preLn = '\n'
		if (logPrint):
			if (logPrintDate):
				print(preLn+time.strftime(LOG_TIME_FORMAT)+logText)
			else:
				print(preLn+logText)
		if (logFile):
			if not os.path.exists(LOG_PATH):
				os.makedirs(LOG_PATH)
			f = open(LOG_PATH+'/'+LOG_FILE, 'a')
			if (logFileDate):
				f.write(preLn+time.strftime(LOG_TIME_FORMAT)+logText+'\n')
			else:
				f.write(preLn+logText+'\n')
			f.close()
