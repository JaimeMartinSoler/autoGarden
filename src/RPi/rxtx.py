
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
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev
import time
import sqlite3
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
from action import *
from glob import *
from DBmanager import *
from actionManager import *




# ----------------------------------------------------------------------
# PARAMETERS

# NRF24L01
PAYLOAD_MAX_SIZE = 32		# defined by NRF24 datasheet
PAYLOAD_ACK_MAX_SIZE = 32	# defined by NRF24 datasheet




# ----------------------------------------------------------------------
# FUNCTIONS

# -------------------------------------
# setup_NRF24(NRF24)
def setup_GPIO():
	# GPIO as BCM mode as per lib_nrf24 requires
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	
# -------------------------------------
# setup_NRF24(NRF24)
def setup_NRF24(radio):

	# parameters: NRF24L01 communication
	pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]
	PIPE_R = 1
	PIPE_W = 0
	# parameters: NRF24L01 pins (CE) and spidev file
	SPIDEV_FILE = 0 
	PIN_CE_BCM = 17
	
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
# intArrayToString(intArray)
# this is used after radio.read(), which returns an array of integer representing a string
def intArrayToString(intArray = []):
	s = ''
	for i in intArray:
		s += chr(i)
	return s


# -------------------------------------
# Function stringToIntArray(s,size)
# used to ease the process of radio.write(), which better requires an array of integers
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
# This is the main funcion and is meant to be executed as a thread
# Receives and manages a radio message, creating and executing the necessary Actions
# return: True(rx success), False(rx failed)
def rx(rxLoop=True):

	# parameters DBconn, DBcursor, radio
	DBconn = sqlite3.connect(DB_FILE_NAME_FULL)
	DBcursor = DBconn.cursor()
	radio = NRF24(GPIO, spidev.SpiDev())
	
	# setup DBconn, DBcursor, GPIO
	setup_GPIO()
	setup_NRF24(radio)
	DBsetup(DBconn, DBcursor)
	
	# rx loop (if !rxLoop it breaks at the bottom)
	while (PROCESS.isAlive):
	
		# RX start listening TX
		radio.startListening();

		# RX loop: wait for a message
		LOG(LOG_INF, "  RX waiting message...");
		while (not radio.available()):
			# Check PROCESS.isAlive
			if (not PROCESS.isAlive):
				return False
			# Check Normal Action to be transmitted, managed from manageNormalAction thread
			if (txNormalAction.txReadyToTx and txNormalAction.txSuccess<=0):
				tx(radio,txNormalAction)	# startListeningAuto=True by default
			# Check Twitter Action to be transmitted, managed from twitterManagerLoop thread
			elif (txTwitterAction.txReadyToTx and txTwitterAction.txSuccess<=0):
				tx(radio,txTwitterAction)	# startListeningAuto=True by default
			# delay
			time.sleep(0.010)

		# ACK_TX payload before RX
		# issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
		strAckTx = 'ACK to Temp from RPi'
		intAckTx = stringToIntArray(strAckTx)
		radio.writeAckPayload(1, intAckTx, len(intAckTx))

		# RX the message (cleaning non-printable characters and the whitespace)
		intMsgRx = []
		radio.read(intMsgRx, radio.getDynamicPayloadSize())
		strMsgRx = intArrayToString(intMsgRx)
		strMsgRx = ''.join([c for c in strMsgRx if ord(c) >= ASCII_PRINT_MIN and ord(c) <= ASCII_PRINT_MAX])
		LOG(LOG_INF, "RX: \"{}\"".format(strMsgRx))
		LOG(LOG_INF, "  ACK_TX_payload: \"{}\"".format(strAckTx))
		
		# Action: create and manage actions
		rxAction.set(text=strMsgRx)
		if (rxAction.getRxBoardId()==BOARD_ID):
			rxType = rxAction.getType()
			# rxNormalAction
			if (rxType==TYPE_NORMAL_L or rxType==TYPE_NORMAL_S):
				rxNormalAction.set(copy=rxAction)
				rxNormalAction.rxReadyToExec = True
				execute(radio,rxNormalAction, DBconn, DBcursor)
			# rxTwitterAction
			elif (rxType==TYPE_TWITTER_L or rxType==TYPE_TWITTER_S):
				rxTwitterAction.set(copy=rxAction)
				rxTwitterAction.rxReadyToExec = True
				execute(radio,rxTwitterAction, DBconn, DBcursor)
			# rxArduinoAction
			elif (rxType==TYPE_ARDUINO_L or rxType==TYPE_ARDUINO_S):
				rxArduinoAction.set(copy=rxAction)
				rxArduinoAction.rxReadyToExec = True
				execute(radio,rxArduinoAction, DBconn, DBcursor)
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
def execute(radio, action, DBconn, DBcursor):

	LOG(LOG_INF, "  Action to execute: \"{}\"".format(action.text));

	# check action.validated
	if (not action.validated):
		LOG(LOG_WAR, "<<< WARNING: Action \"{}\" NOT executed, Action NOT Validated >>>".format(action.text))
		return False
	# check action.rxReadyToExec
	if (not action.rxReadyToExec):
		LOG(LOG_WAR, "<<< WARNING: Action \"{}\" NOT executed, Action NOT Ready to Exec >>>".format(action.text))
		return False
		
	# get parameters
	id = action.getId()
	txBoardId = action.getTxBoardId()
	rxBoardId = action.getRxBoardId()
	type = action.getType()
	type_L = action.getType_L()
	func = action.getFunc()
	paramNum = action.getParamNum()
	wpar = action.getWpar()
	wparId = action.getWparId()
	value = action.getValue()
	
	# log parameters
	LOG(LOG_DET, "    ID: \"{}\"".format(id));
	LOG(LOG_DET, "    txBoardId: \"{}\"".format(txBoardId))
	LOG(LOG_DET, "    rxBoardId: \"{}\"".format(rxBoardId))
	LOG(LOG_DET, "    type: \"{}\"".format(type))
	LOG(LOG_DET, "    function: \"{}\"".format(func))
	LOG(LOG_DET, "    paramNum: {}".format(paramNum))
	LOG(LOG_DET, "    weather param: \"{}\"".format(wpar))
	LOG(LOG_DET, "    weather param id: \"{}\"".format(wparId))
	LOG(LOG_DET, "    value: \"{}\"".format(value))
	
	# BOARD_ID = RX
	if (rxBoardId==BOARD_ID):

		# FUNC = SET
		if (func==FUNC_SET_L or func==FUNC_SET_S):

			# PARAM NUM = 3
			if (paramNum==3):

				# WPAR = TEMP
				if (wpar==WPAR_TEMP_L or wpar==WPAR_TEMP_S):

					# WPARID = LM35
					if (wparId==WPARID_TEMP_LM35_L or wparId==WPARID_TEMP_LM35_S):
						DBinsert(DBconn, DBcursor, type_L, WPAR_TEMP_L, WPARID_TEMP_LM35_L, valueReal=float(value))
						action.rxExec += 1
						return True

					# WPARID = DHT (for WPAR = TEMP)
					elif (wparId==WPARID_TEMP_DHT_L or wparId==WPARID_TEMP_DHT_S):
						DBinsert(DBconn, DBcursor, type_L, WPAR_TEMP_L, WPARID_TEMP_DHT_L, valueReal=float(value))
						action.rxExec += 1
						return True

				# WPAR = HUMI
				elif (wpar==WPAR_HUMI_L or wpar==WPAR_HUMI_S):
				
					# WPARID = DHT (for WPAR = HUMI)
					if (wparId==WPARID_HUMI_DHT_L or wparId==WPARID_HUMI_DHT_S):
						DBinsert(DBconn, DBcursor, type_L, WPAR_HUMI_L, WPARID_HUMI_DHT_L, valueReal=float(value))
						action.rxExec += 1
						return True

	# BOARD_ID = TX
	elif (txBoardId==BOARD_ID):
		if (action.txReadyToTx and action.txSuccess<=0):
			tx(radio, action)
			if (action.txSuccess>0):
				LOG(LOG_DET, "  Action to execute: \"{}\" successfully executed".format(action.text))
				action.rxExec += 1
				return True

	LOG(LOG_WAR, "<<< WARNING: Action to execute: \"{}\" was NOT successfully executed >>>".format(action.text));
	return False

	
