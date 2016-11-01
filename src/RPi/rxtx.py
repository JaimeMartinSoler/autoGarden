
# ----------------------------------------------------------------------
# --- rxtx.py                                                        ---
# ----------------------------------------------------------------------
# --- High level static functions to deal with RX, TX and also       ---
# --- generation and execution of received actions                   ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-10-25                                             ---
# ----------------------------------------------------------------------



# ----------------------------------------------------------------------
# IMPORTS
from lib_nrf24 import NRF24
import spidev
import os
import time
import sqlite3
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
from action import *
from glob import *



# ----------------------------------------------------------------------
# PARAMETERS

# NRF24L01 communication
pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]
PIPE_R = 1
PIPE_W = 0
role = 0
ROLE_TX = 0
ROLE_RX = 1
PAYLOAD_MAX_SIZE = 32		# defined by NRF24 datasheet
PAYLOAD_ACK_MAX_SIZE = 32	# defined by NRF24 datasheet

# NRF24L01 pins (CE) and spidev file
SPIDEV_FILE = 0 
PIN_CE_BCM = 17




# ----------------------------------------------------------------------
# FUNCTIONS


# -------------------------------------
# setup_NRF24(NRF24)
def setup_NRF24(radio):
	# NRF24L01 begin
	radio.begin(SPIDEV_FILE, PIN_CE_BCM)
	# message and ACK
	radio.setPayloadSize(PAYLOAD_MAX_SIZE)
	radio.enableDynamicPayloads()	# instead of: radio.setPayloadSize(int)
	radio.setAutoAck(True)
	radio.enableAckPayload()
	radio.setRetries(1,15);         # min ms between retries, max number of retries
	# channel and pipes
	radio.setChannel(0x76)
	radio.openReadingPipe(1, pipes[PIPE_R])
	radio.openWritingPipe(pipes[PIPE_W])
	# rate, power
	radio.setDataRate(NRF24.BR_1MBPS)	# with RF24_250KBPS <10% success...
	radio.setPALevel(NRF24.PA_HIGH)
	# print details
	radio.printDetails()

# -------------------------------------
# Function intArrayToString(intArray)
def intArrayToString(intArray = []):
	s = ''
	for i in intArray:
		s += chr(i)
	return s


# -------------------------------------
# Function stringToIntArray(s,size)
def stringToIntArray(s,size=PAYLOAD_ACK_MAX_SIZE):
	charArray = list(s)
	arrayLen = len(charArray)
	intArray = [None] * arrayLen
	for idx in range(arrayLen):
		intArray[idx] = ord(charArray[idx])
	if (size < arrayLen):
		return intArray[0:size]
	elif (size > arrayLen):
		return intArray + ([0]*(size-arrayLen))
	return intArray


# -------------------------------------
# rx(NRF24, rxLoop=False)
# Receive and manage radio message, creating and executing the necessary Actions
# return: True(rx success), False(rx failed)
def rx(radio, rxLoop=False):

	# rx loop (if !rxLoop it breaks at the bottom)
	while (True):

		# RX start listening TX
		radio.startListening();

		# RX loop: wait for a message
		LOG(LOG_INF, "  RX waiting message...");
		while (not radio.available()):
			# Check Normal Action to be transmitted, managed from manageNormalAction thread (TODO)
			if (txNormalAction.txReadyToTx and txNormalAction.txSuccess<=0):
				tx(radio,txNormalAction)	# startListeningAuto=True by default
			# Check Normal Action to be transmitted, managed from twitterManagerLoop thread (TODO)
			elif (txTwitterAction.txReadyToTx and txTwitterAction.txSuccess<=0):
				tx(radio,txTwitterAction)	# startListeningAuto=True by default
			# sleep
			time.sleep(0.010)

		# ACK_TX payload before RX
		# issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
		strAckTx = 'ACK to Temp from RPi'
		intAckTx = stringToIntArray(strAckTx)
		radio.writeAckPayload(1, intAckTx, len(intAckTx))

		# RX the message
		intMsgRx = []
		radio.read(intMsgRx, radio.getDynamicPayloadSize())
		strMsgRx = intArrayToString(intMsgRx)
		LOG(LOG_INF, "RX: \"{}\"".format(strMsgRx))
		LOG(LOG_INF, "  ACK_TX_payload: \"{}\"".format(strAckTx))
		
		# Action: create and manage actions
		rxAction.set(text=strMsgRx)
		if (rxAction.getRxBoardId()==BOARD_ID):
			rxType = rxAction.getType()
			if (rxType==TYPE_NORMAL_L or rxType==TYPE_NORMAL_S):
				rxNormalAction.set(copy=rxAction)
				rxNormalAction.rxReadyToExec = True
				execute(radio,rxNormalAction)
			elif (rxType==TYPE_TWITTER_L or rxType==TYPE_TWITTER_S):
				rxTwitterAction.set(copy=rxAction)
				rxTwitterAction.rxReadyToExec = True
				execute(radio,rxTwitterAction)
			elif (rxType==TYPE_ARDUINO_L or rxType==TYPE_ARDUINO_S):
				rxArduinoAction.set(copy=rxAction)
				rxArduinoAction.rxReadyToExec = True
				execute(radio,rxArduinoAction)
			else:
				LOG(LOG_WAR,"<<< WARNING: RX Action mode unknown: \"{}\" >>>".format(rxType))

		# keep/breake infinite loop
		if (not rxLoop):
			return True

	# if RX loop is broken, return false
	return False;


# -------------------------------------
# tx(NRF24, Action)
# Transmit the passed Action
# return: true(ACK_RX), false(NO_ACK_RX)
def tx(radio, action, startListeningAuto=True):

	# check if action is validated
	if (not action.validated):
		LOG(LOG_WAR, "<<< WARNING: Action \"{}\" NOT TX, Action NOT Validated >>>".format(action.text))
		return False

	# wait a bit for the receiver to get ready for RX mode, just in case
	time.sleep(0.020)

	# TX stop listening RX
	radio.stopListening();
	
	# TX message
	intMsgTx = stringToIntArray(action.text)
	LOG(LOG_INF, "TX: \"{}\"".format(action.text), logPreLn=True)
	# No ACK received, return False:
	action.txAttempts += 1
	if(radio.write(intMsgTx) == 0):
		LOG(LOG_WAR, "<<< WARNING:  ACK_RX: NOT received >>>")
		if (startListeningAuto):
			radio.startListening()
		return False
	
	# ACK_RX, return True:
	# issue!!!: when a row of msg is read, after TX stops, RX keeps reading ACKs for 2-3 times
	else:
		action.txSuccess += 1
		# ACK_RX (ACK payload OK):
		# issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
		if (radio.isAckPayloadAvailable()):
			intAckRx = []
			radio.read(intAckRx, radio.getDynamicPayloadSize())
			strAckRx = intArrayToString(intAckRx)
			LOG(LOG_INF, "  ACK_RX: YES (payload=\"{}\")".format(strAckRx))
		# ACK_RX (ACK payload <empty>): 
		else:
			LOG(LOG_INF, "  ACK_RX: YES (ack_payload=<empty>)")
		# return True
		if (startListeningAuto):
			radio.startListening()
		return True
		

# -------------------------------------	
# execute(NRF24,Action)
# Execute and Action, both received and meant to be transmitted
# return: true(exec success), false(exec failed)
def execute(radio, action):

	LOG(LOG_INF, "  Action to execute: \"{}\"".format(action.text));

	# check action.validated
	if (not action.validated):
		LOG(LOG_WAR, "<<< WARNING: Action \"{}\" NOT executed, Action NOT Validated >>>".format(action.text))
		return False
	# check action.rxReadyToExec
	if (not action.rxReadyToExec):
		LOG(LOG_WAR, "<<< WARNING: Action \"{}\" NOT executed, Action NOT Ready to Exec >>>".format(action.text))
		return False
	
	# RX: "III,TT,<AO>,MM,FFF,..."
	LOG(LOG_DET, "    txBoardId: \"{}\"".format(action.getTxBoardId()))
	LOG(LOG_DET, "    rxBoardId: \"{}\"".format(action.getRxBoardId()))
	if (action.getRxBoardId()==BOARD_ID):

		# "III,TT,<AO>,MM,<SET>,..."
		LOG(LOG_DET, "    function: \"{}\"".format(action.getFunc_L()))
		if (action.getFunc_L()==FUNC_SET_L):

			# "III,TT,<AO>,MM,<SET>,WWWW,IIII"
			LOG(LOG_DET, "    paramNum: {}".format(action.getParamNum()))
			if (action.getParamNum()==3):

				# "III,TT,<AO>,MM,<SET>,<T/TEMP>,IIII"
				LOG(LOG_DET, "    weather param: \"{}\"".format(action.getWpar_L()))
				if (action.getWpar_L()==WPAR_TEMP_L):

					# "III,TT,<AO>,MM,<SET>,<T/TEMP>,<A/AIR>"
					LOG(LOG_DET, "    weather param id: \"{}\"".format(action.getWparId_L()))
					if (action.getWparId_L()==WPARID_TEMP_LM35_L):
						DB_insert(action.getType_L(), action.getWpar_L(), action.getWparId_L(), valueRea=float(action.getValue()))
						action.rxExec += 1
						return True

	# TX: "III,<AO>,RR,MM,..."
	elif (action.getTxBoardId()==BOARD_ID):
		if (action.txReadyToTx and action.txSuccess<=0):
			tx(radio, action)
			if (action.txSuccess>0):
				LOG(LOG_DET, "  Action to execute: \"{}\" successfully executed".format(action.text))
				action.rxExec += 1
				return True

	LOG(LOG_WAR, "<<< WARNING: Action to execute: \"{}\" was NOT successfully executed >>>".format(action.text));
	return False

	


# -------------------------------------
# setup_DB()
def setup_DB():
	if (not os.path.exists(DB_PATH)):
		os.makedirs(DB_PATH)
	DB_CONN = sqlite3.connect(DB_FULL_PATH)
	db_cursor = DB_CONN.cursor()
	db_cursor.execute('''
		CREATE TABLE IF NOT EXISTS WEATHER (
			ID INTEGER PRIMARY KEY AUTOINCREMENT,
			DATE TEXT NOT NULL,
			TIME TEXT NOT NULL,
			TYPE TEXT NOT NULL,
			WPAR TEXT NOT NULL,
			WPARID TEXT NOT NULL,
			VALUE_INT INTEGER,
			VALUE_REA REAL,
			VALUE_STR TEXT
		);
	''')
	DB_CONN.commit()
	#DB_CONN.close()


# -------------------------------------
# DB_insert(type)
def DB_insert(type, wpar, wparId, valueInt=None, valueRea=None, valueStr=None):
	db_row = (time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), type, wpar, wparId, valueInt, valueRea, valueStr)
	db_cursor = DB_CONN.cursor()
	db_cursor.execute('INSERT INTO WEATHER(DATE,TIME,TYPE,WPAR,WPARID,VALUE_INT,VALUE_REA,VALUE_STR) VALUES (?,?,?,?,?,?,?,?)', db_row)
	DB_CONN.commit()

	
	

# -------------------------------------
# generateAction(Action)
# Checks the status of the sensors and autonomously generates and Action, if needed
# This function is meant to be executed in the RX wait loop every few milliseconds
# return: true(action generated), false(no action generated)
def manageTxNormalAction():
	# setup
	time.sleep(3.000)
	stringBaseId = "000"
	countId = 0
	txNormalAction.set(stringBaseId+",R0,A0,NR,GET,TEMP,AIR")
	txNormalAction.txReadyToTx = True
	# loop
	while(True):
		while(txNormalAction.txReadyToTx and txNormalAction.txSuccess<=0):
			time.sleep(0.100)
		countId += 1
		txNormalAction.set(idAdd(stringBaseId,countId)+",R0,A0,NR,GET,TEMP,AIR")
		txNormalAction.txReadyToTx = True
		time.sleep(3.0)
		
