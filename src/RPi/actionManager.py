#!/usr/bin/python

# ----------------------------------------------------------------------
# --- actionManager.py                                               ---
# ----------------------------------------------------------------------
# --- High level interacion of tx and rx action objects              ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-11-15                                             ---
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# IMPORTS
from glob import *
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
from action import *
import time




# ----------------------------------------------------------------------
# PARAMETERS

# Action Tags
ACTION_TYPES_GLOBAL = 3
ACTION_NORMAL_ID = 0
ACTION_TWITTER_ID = 1
ACTION_ARDUINO_ID = 2

# Actions
rxAction = Action()			# Action for RX general propose
rxNormalAction = Action()	# Action for RX Normal actions, answers to requests from RPi DB,timers checking module
rxTwitterAction = Action()	# Action for RX Twitter actions, answers to requests from RPi Twitter checking module
rxArduinoAction = Action()	# Action for RX Arduino actions, urgents messages sent by Arduino
txNormalAction = Action()	# Action for TX Normal actions, requests from RPi DB,timers checking module
txTwitterAction = Action()	# Action for TX Twitter actions, requests from RPi Twitter checking module




# ----------------------------------------------------------------------
# FUNCTIONS

# setTXwaitRX(txAction, rxAction, txActionText, timeOut=5000, autoIncrement=True)
#	this function sets a txAction with txActionText and waits for the corrensponding rxAction to be ready,
#   both txAction, rxAction must be updated externally by a rxrx.py thread.
# 		raise RuntimeError: if (not PROCESS.isAlive)
# 		raise TimeoutError: if (wait>timeOut)
# 		raise ValueError: if (after wait, rxAction.getId() is not the expected)
def setTXwaitRX(txAction, rxAction, txActionText, timeOut=5000, autoIncrement=True, checkRXid=True):

	# set current millis
	millis = int(round(time.time()*1000))
	
	# clear rx and set tx objects
	txId = txAction.getId()		# backup of txAction.ID, in case of autoincrement
	rxAction.set()				# .rxReadyToExec=False, .rxExec=0
	txAction.set(txActionText)	# .txReadyToTx=False, .txSuccess=0
	
	# autoIncrement
	if (autoIncrement):
		txAction.setId(idAdd(txId,ACTION_TYPES_GLOBAL*2))
	txAction.txReadyToTx = True
	
	# wait for txAction and rxAction to be ready (rxtx.py has to deal with txAction, rxAction in another thread)
	while(txAction.txSuccess<=0 or rxAction.rxExec<=0):
		if (not PROCESS.isAlive):
			raise RuntimeError("PROCESS.isAlive=false")
		if ((int(round(time.time()*1000)) - millis) >= timeOut):
			raise OSError("timeOut ({}) reached. txSuccess={}, rxExec={}".format(timeOut,txAction.txSuccess,rxAction.rxExec))
		time.sleep(0.100)

	# check the rxAction.getId() is the expected
	if (checkRXid and (idAdd(txAction.getId(),ACTION_TYPES_GLOBAL) != rxAction.getId())):
		raise ValueError("expected rxAction.ID:\"{}\", recieved rxAction.ID:\"{}\"".format(idAdd(txAction.getId(),ACTION_TYPES_GLOBAL),rxAction.getId()))
	
	