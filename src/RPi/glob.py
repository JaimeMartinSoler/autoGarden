# ----------------------------------------------------------------------
# --- global.cpp                                                     ---
# ----------------------------------------------------------------------
# --- Global variables     										     ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-10-25                                             ---
# ----------------------------------------------------------------------


# set "utf-8" encoding
# http://stackoverflow.com/questions/9644099/python-ascii-codec-cant-decode-byte
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


# ----------------------------------------------------------------------
# IMPORTS
import inspect
import os
import json
import shutil





# ----------------------------------------------------------------------
# PROCESS: CLASS AND OBJECT
class Process:
	mainPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	def __init__(self):
		mainPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# PROCESS: OBJECT
PROCESS = Process()




# log requires PROCESS
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF


# ----------------------------------------------------------------------
# STATUS: CLASS AND OBJECT
class Status:

	# non-JSON parameters:
	statusFileNameFull = "{}/data/STATUS.json"
	statusDefFileNameFull = "{}/data/STATUS_def.json"
	modificationTime = 0 # seconds since epoch
	# dataJSON parameter:
	dataJSON = ""
		# isAlive = True
		# twitterEnable = True
		# ipCamRotation = 0
	
	# __init__(self)
	def __init__(self):
		# non-JSON parameters:
		self.statusFileNameFull = self.statusFileNameFull.format(PROCESS.mainPath)
		self.statusDefFileNameFull = self.statusDefFileNameFull.format(PROCESS.mainPath)
		self.modificationTime = os.path.getmtime(self.statusFileNameFull)
		# dataJSON parameter:
		self.dataJSONread()
		
	# dataJSONread (self)
	def dataJSONread(self):
		with open(self.statusFileNameFull, 'r') as dataFile:
			self.dataJSON = json.load(dataFile)
	
	# get (self, parameter)
	# check update in modification time, may no need to open
	def get(self, parameter):
		try:
			modificationTimeCurrent = os.path.getmtime(self.statusFileNameFull)
		except:
			LOG(LOG_WAR, "<<< WARNING: unable to read file \"{}\">>>".format(self.statusFileNameFull))
			modificationTimeCurrent = os.path.getmtime(self.statusDefFileNameFull)
		if (modificationTimeCurrent > self.modificationTime):
			self.modificationTime = modificationTimeCurrent
			self.dataJSONread()
		return self.dataJSON[parameter]
	
	# set(self, parameter, value)
	def set(self, parameter, value):
		self.dataJSON[parameter] = value
		with open(self.statusFileNameFull, 'w') as dataFile:
			json.dump(self.dataJSON, dataFile)

	# fileToDefault(self)
	def fileToDefault(self):
		try:
			shutil.copy(self.statusDefFileNameFull, self.statusFileNameFull)
		except:
			LOG(LOG_WAR, "<<< WARNING: unable to copy file \"{}\">>>".format(self.statusDefFileNameFull))


# ----------------------------------------------------------------------
# STATUS: CLASS AND OBJECT
class TweetData:

	# non-JSON parameters:
	tweetDataFileNameFull = "{}/data/TWEETDATA.json"
	modificationTime = 0 # seconds since epoch
	# dataJSON parameter:
	dataJSON = ""
	
	# __init__(self)
	def __init__(self):
		# non-JSON parameters:
		self.tweetDataFileNameFull = self.tweetDataFileNameFull.format(PROCESS.mainPath)
		self.modificationTime = os.path.getmtime(self.tweetDataFileNameFull)
		# dataJSON parameter:
		self.dataJSONread()
		
	# dataJSONread (self)
	def dataJSONread(self):
		with open(self.tweetDataFileNameFull, 'r') as dataFile:
			self.dataJSON = json.load(dataFile)
	
	# get (self, parameter)
	# check update in modification time, may no need to open
	def get(self, p0, p1=None, p2=None, p3=None, p4=None, p5=None):
		try:
			modificationTimeCurrent = os.path.getmtime(self.tweetDataFileNameFull)
		except:
			LOG(LOG_WAR, "<<< WARNING: unable to read file \"{}\">>>".format(self.tweetDataFileNameFull))
		if (modificationTimeCurrent > self.modificationTime):
			self.modificationTime = modificationTimeCurrent
			self.dataJSONread()
		value = self.dataJSON[p0]
		if (p1 is not None):
			value = value[p1]
			if (p2 is not None):
				value = value[p2]
				if (p3 is not None):
					value = value[p3]
					if (p4 is not None):
						value = value[p4]
						if (p5 is not None):
							value = value[p5]
		return value

						
			

# STATUS: OBJECT
# PROCESS.mainPath must exist before Status() is executed
STATUS = Status()		
TWEETDATA = TweetData()

