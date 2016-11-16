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
ACTIONS_TX_GLOBAL = 3




# ----------------------------------------------------------------------
# FUNCTIONS

# setTXwaitRX(txAction, rxAction, txActionText, timeOut=5000, autoIncrement=True)
#	this function sets a txAction with txActionText and waits for the corrensponding rxAction to be ready,
#   both txAction, rxAction must be updated externally by a rxrx.py thread.
# 		raise ProcessLookupError: if (not PROCESS.isAlive)
# 		raise TimeoutError: if (wait>timeOut)
# 		raise ValueError: if (after wait, rxAction.getId() is not the expected)
def setTXwaitRX(txAction, rxAction, txActionText, timeOut=5000, autoIncrement=True, checkRXid=True):

	# set current millis
	millis = int(round(time.time()*1000))
	
	# clear rx and set tx objects
	rxAction.set()				# .rxReadyToExec=False, .rxExec=0
	txAction.set(txActionText)	# .txReadyToTx=False, .txSuccess=0
	if (autoIncrement):
		txAction.setId(idAdd(txAction.getId(),ACTIONS_TX_GLOBAL*2))	# TODO: action.setId(String), ACTIONS_TX_GLOBAL
	txAction.txReadyToTx = True
	
	# wait for txAction and rxAction to be ready (rxtx.py has to deal with txAction, rxAction in another thread)
	while(txAction.txSuccess<=0 or rxAction.rxExec<=0):
		if (not PROCESS.isAlive):
			raise ProcessLookupError("PROCESS.isAlive=false")
		if ((int(round(time.time()*1000)) - millis) >= timeOut):
			raise TimeoutError("timeOut ("+timeOut+") reached")
		time.sleep(0.100)

	# check the rxAction.getId() is the expected
	if (checkRXid and (idAdd(txAction.getId(),ACTIONS_TX_GLOBAL) != rxAction.getId())):
		raise ValueError("expected rxAction.ID: \""+idAdd(txAction.getId(),ACTIONS_TX_GLOBAL)+"\"\nrecieved rxAction.ID: \""+rxAction.getId()+"\"")
	
	

