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

# getToDB(wpar, wparId, type, id='XXX', boardIdTx=BOARD_ID, boardIdRx=BOARD_A0_ID, func=FUNC_GET_S, timeOut=5000, autoIncrement=True, checkRXid=True)
#	this function sets the corresponding txAction/rxAction (according to type) and waits for the rxAction to be ready,
#   both txAction, rxAction must be updated externally by the rxrx.py thread.
def getToDB(wpar, wparId, type=TYPE_NORMAL_L, id='XXX', boardIdTx=BOARD_ID, boardIdRx=BOARD_A0_ID, func=FUNC_GET_S, append='', timeOut=5000, autoIncrement=True, checkRXid=True):

	# set current millis
	millis = int(round(time.time()*1000))
	
	# get the tx/rx actions (normal action by default)
	txAction = txNormalAction
	rxAction = rxNormalAction
	if (getType_L(type)==TYPE_TWITTER_L):
		txAction = txTwitterAction
		rxAction = rxTwitterAction
	
	# build the txActionText
	txActionText = '{},{},{},{},{},{},{}{}'.format(id, boardIdTx, boardIdRx, getType_S(type), getFunc_S(func), getWpar_L(wpar), getWparId_L(wparId), append)

	# clear rx and set tx objects
	txId = txAction.getId()		# backup of txAction.ID, in case of autoincrement
	rxAction.set()				# .rxReadyToExec=False, .rxExec=0
	txAction.set(txActionText)	# .txReadyToTx=False, .txSuccess=0
	
	# autoIncrement
	if (autoIncrement):
		txAction.setId(idAdd(txId,ACTION_TYPES_GLOBAL*2))
	txAction.txReadyToTx = True

	# wait for txAction and rxAction to be ready (rxtx.py has to deal with txAction, rxAction in another thread, it manages the DB inserts)
	while(txAction.txSuccess<=0 or rxAction.rxExec<=0):
		if ((int(round(time.time()*1000)) - millis) >= timeOut):
			LOG(LOG_WAR, "<<< WARNING: timeOut ({}) reached for \"{}\". txSuccess={}, rxExec={} >>>".format(timeOut, txActionText, txAction.txSuccess, rxAction.rxExec))
			return False
		time.sleep(0.100)

	# check the rxAction.getId() is the expected
	if (checkRXid and (idAdd(txAction.getId(),ACTION_TYPES_GLOBAL) != rxAction.getId())):
		LOG(LOG_WAR, "<<< WARNING: for \"{}\", expected rxAction.ID:\"{}\", recieved rxAction.ID:\"{}\" >>>".format(txActionText, idAdd(txAction.getId(),ACTION_TYPES_GLOBAL), rxAction.getId()))
		return False
	
	return True

	