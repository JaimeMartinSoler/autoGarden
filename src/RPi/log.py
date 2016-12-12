#!/usr/bin/python

# ----------------------------------------------------------------------
# IMPORTS
from glob import *
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
LOG_LVL = LOG_DET	# the current log level

# LOG_PATH
LOG_PATH_REL = 'log'
LOG_PATH_FULL = PROCESS.mainPath + '/' + LOG_PATH_REL
# LOG_FILE
LOG_FILE_NAME_FORMAT = 'log_{}.txt'
LOG_FILE_NAME_TIME_FORMAT = '%Y%m%d'
LOG_FILE_NAME = LOG_FILE_NAME_FORMAT.format(time.strftime(LOG_FILE_NAME_TIME_FORMAT))
LOG_FILE_NAME_FULL = LOG_PATH_FULL + '/' + LOG_FILE_NAME
# LOG_TEXT
LOG_TEXT_DATE_FORMAT = '[%Y-%m-%d %H:%M:%S]: '




# ----------------------------------------------------------------------
# FUNCTIONS

# -------------------------------------
# LOG
def LOG(logLevel, logText, logPrint=True, logFile=True, logPrintDate=True, logFileDate=True, logPreLn=False):
	# global references possibly modified
	global LOG_FILE_NAME, LOG_FILE_NAME_FULL
	# log just if logLevel >= LOG_LVL
	if (logLevel >= LOG_LVL):
		preLn = ''
		# set preLn = '\n', if logPreLn
		if (logPreLn):
			preLn = '\n'
		# logPrint: manage log terminal print
		if (logPrint):
			if (logPrintDate):
				print(preLn+time.strftime(LOG_TEXT_DATE_FORMAT)+logText)
			else:
				print(preLn+logText)
		# logFile: manage file log
		if (logFile):
			# check if LOG_PATH_FULL exists, create it if it does not
			if not os.path.exists(LOG_PATH_FULL):
				os.makedirs(LOG_PATH_FULL)
			# check if LOG_FILE_NAME(_FULL)has changed (because it is a new date)
			if (LOG_FILE_NAME != LOG_FILE_NAME_FORMAT.format(time.strftime(LOG_FILE_NAME_TIME_FORMAT))):
				LOG_FILE_NAME = LOG_FILE_NAME_FORMAT.format(time.strftime(LOG_FILE_NAME_TIME_FORMAT))
				LOG_FILE_NAME_FULL = LOG_PATH_FULL + '/' + LOG_FILE_NAME
			# open LOG_FILE_NAME_FULL in 'append' mode write the logText
			f = open(LOG_FILE_NAME_FULL, 'a')
			if (logFileDate):
				f.write(preLn+time.strftime(LOG_TEXT_DATE_FORMAT)+logText+'\n')
			else:
				f.write(preLn+logText+'\n')
			f.close()
