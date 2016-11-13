#!/usr/bin/python

# ----------------------------------------------------------------------
# --- action.py                                                      ---
# ----------------------------------------------------------------------
# --- Action objects, to manage RX/TX messages, meant for NRF24L01   ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-10-13                                             ---
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# IMPORTS
from glob import *
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF




# ----------------------------------------------------------------------
# PARAMETERS CONSTANTS

# separator and max size
ACTION_ANY_CHAR = '*'
ACTION_SEPARATOR = ','
ACTION_MAX_SIZE = 32  	# this should be: (Sensors::NRF24_PAYLOAD_MAX_SIZE)
FIXED_PARAMETERS = 5

# ASCII
ASCII_PRINT_MIN = 33   # '!' first printable ASCII character
ASCII_PRINT_MAX = 126  # '~' last  printable ASCII character
ASCII_PRINT_RANGE = ASCII_PRINT_MAX - ASCII_PRINT_MIN + 1

# ID
ID_MAX_SIZE = 3 # unlike C++, here we do NOT have to include the null char '\0')
ID_POS = 0      # position in payload char array
		# this must be 0, if we change it we would have to change more code,
		# the reason is that ID admits ',' as value but also is the separator,
		# so ID is treated specially in some parts of the code in this class
ID_MAX = (ASCII_PRINT_RANGE * ASCII_PRINT_RANGE * ASCII_PRINT_RANGE) - 1

# Board ID
BOARD_ID_MAX_SIZE = 2 # unlike C++, here we do NOT have to include the null char '\0')
BOARD_ID_TX_POS = 1   # position in payload char array
BOARD_ID_RX_POS = 2   # position in payload char array
BOARD_ID ='R0'
BOARD_A0_ID = 'A0'

# Type
TYPE_MAX_SIZE = 2 # unlike C++, here we do NOT have to include the null char '\0')
TYPE_POS = 3      # position in payload char array
# Type Parameters: Long (length<=2)
TYPE_NORMAL_L = 'NR'
TYPE_TWITTER_L = 'TW'
TYPE_ARDUINO_L = 'AR'
# Type Parameters: Short (length=1)
TYPE_NORMAL_S = 'N'
TYPE_TWITTER_S = 'T'
TYPE_ARDUINO_S = 'A'

# Function Parameters
FUNC_MAX_SIZE = 4   # unlike C++, here we do NOT have to include the null char '\0')
FUNC_POS = 4        # position in payload char array
# Function Parameters: Long (length<=4)
FUNC_GET_L = 'GET'
FUNC_SET_L = 'SET'
# Function Parameters: Short (length=1)
FUNC_GET_S = 'G'
FUNC_SET_S = 'S'

# Weather Parameters
WPAR_MAX_SIZE = 4   # unlike C++, here we do NOT have to include the null char '\0')
WPAR_POS = 5        # position in payload char array
# Weather Parameters: Long (length<=4)
WPAR_TEMP_L = 'TEMP'
WPAR_HUMI_L = 'HUMI'
# Weather Parameters: Short (length=1)
WPAR_TEMP_S = 'T'
WPAR_HUMI_S = 'H'

# Sensor Id Parameters
WPARID_MAX_SIZE = 4   # unlike C++, here we do NOT have to include the null char '\0')
WPARID_POS = 6        # position in payload char array
# Sensor Id Parameters: Long (length<=4)
WPARID_TEMP_LM35_L = 'AIR'
# Weather Parameters: Short (length=1)
WPARID_TEMP_LM35_S = 'A'

# Value Parameters
VALUE_MAX_SIZE = ACTION_MAX_SIZE  # unlike C++, here we do NOT have to include the null char '\0')
VALUE_POS = 7                     # position in payload char array


	
# ----------------------------------------------------------------------
# FUNCTIONS - STATIC

# -----------------------
# idAdd(String, int)
# It gets the String Id result of the sum of the addition plus strId equivalent.
# (i.e.: idAdd("ABC",1)->"ABD", idAdd("ABC",-2)->"ABA")
# It deals with overflow and negative addition.
# return: strId + addition (taking care of type conversions, etc)
def idAdd(strId, addition):
	intId = idToInt(strId)
	if (intId < 0):
		return 'X'
	intId += addition
	if (intId < 0):
		intId += (ID_MAX+1)
	elif (intId > ID_MAX):
		intId -= (ID_MAX+1)
	return intToId(intId)


# -----------------------
# idToInt(String)
# return: it gets the equivalent int to the String strId.
# (i.e.: idToInt("!!!")->0, idAdd("ABC")->285888, idAdd("~~~")->830583)
def idToInt(strId):
	v = 0
	intId = 0
	if (len(strId) != ID_MAX_SIZE):
		return -1
	for i in range(0,ID_MAX_SIZE):
		v = ord(strId[i]) - ASCII_PRINT_MIN;
		if ((v < 0) or (v > ASCII_PRINT_RANGE)):
			return -1
		intId += (v * (ASCII_PRINT_RANGE**(ID_MAX_SIZE-i-1)))
	return intId


# -----------------------
# intToId(int)
# return: it gets the String equivalent to the int intId.
# (i.e.: idToInt(0)->"!!!", idAdd(285888)->"ABC", idAdd(830583)->"~~~")
def intToId(intId):
	strId = ''
	divisor = 0
	remain = intId
	if ((intId < 0) or (intId > ID_MAX)):
		return 'X'
	for expon in range(ID_MAX_SIZE-1,-1,-1):
		divisor = ASCII_PRINT_RANGE**expon
		strId += chr(ASCII_PRINT_MIN+remain/divisor)
		remain = remain%divisor
	return strId

	
	

# ----------------------------------------------------------------------
# CLASS ACTION
class Action:

    # ----------------------------------------------------------------------
    # PARAMETERS

	# Parameters Payload
	text = [None]*ACTION_MAX_SIZE	# char array with the action message text
	validated = False  				# true: paramters are OK, false: parameters NOT_OK
	# Parameters RX
	rxReadyToExec = False	# true: action ready to be executed, false: not ready
	rxExec = 0				# times the action has been executed
	rxTweet = 0				# times the action has been tweet(ed) (or managed by twitter module)
	# Parameters TX
	txReadyToTx	= False		# true: action ready to be transmitted, false: not ready
	txSuccess = 0 			# number of times this action was successfuly tx
	txAttempts = 0			# number of times this action was attampted to be tx
	
	
	
	
    # ----------------------------------------------------------------------
    # CONSTRUCTOR (it just calls the setter)
	def __init__(self, text=None, copy=None):
		self.set(text, copy)
		
		
		
		
    # ----------------------------------------------------------------------
    # FUNCTIONS - SETTER
	def set(self, text=None, copy=None):
		# Setter Main: set by text
		if (text != None):
			self.text = text
			self.validate()
			self.rxReadyToExec = False
			self.rxExec = 0
			self.rxTweet = 0
			self.txReadyToTx = False
			self.txSuccess = 0
			self.txAttempts = 0
		# Setter Copy: set by actionCopy
		elif (copy != None):
			self.text = copy.text
			self.validated = copy.validated
			self.rxReadyToExec = copy.rxReadyToExec
			self.rxExec = copy.rxExec
			self.rxTweet = copy.rxTweet
			self.txReadyToTx = copy.txReadyToTx
			self.txSuccess = copy.txSuccess
			self.txAttempts = copy.txAttempts
		# Setter Default:
		else:
			self.text = ''
			self.validated = False
			self.rxReadyToExec = False
			self.rxExec = 0
			self.rxTweet = 0
			self.txReadyToTx = False
			self.txSuccess = 0
			self.txAttempts = 0
		
		
		
		
    # ----------------------------------------------------------------------
    # FUNCTIONS - GETTERS
	def getId(self):
		return self.getStringInPos(ID_POS)
	def getTxBoardId(self):
		return self.getStringInPos(BOARD_ID_TX_POS)
	def getRxBoardId(self):
		return self.getStringInPos(BOARD_ID_RX_POS)
	def getType(self):
		return self.getStringInPos(TYPE_POS)
	def getType_S(self):
		type = self.getType()
		if (len(type)>1):
			if (type==TYPE_NORMAL_L):
				return TYPE_NORMAL_S
			elif (type==TYPE_TWITTER_L):
				return TYPE_TWITTER_S
			elif (type==TYPE_ARDUINO_L):
				return TYPE_ARDUINO_S
		else:
			return type
	def getType_L(self):
		type = self.getType()
		if (len(type)<=1):
			if (type==TYPE_NORMAL_S):
				return TYPE_NORMAL_L
			elif (type==TYPE_TWITTER_S):
				return TYPE_TWITTER_L
			elif (type==TYPE_ARDUINO_S):
				return TYPE_ARDUINO_L
		else:
			return type
	def getFunc(self):
		return self.getStringInPos(FUNC_POS)
	def getFunc_S(self):
		func = self.getFunc()
		if (len(func)>1):
			if (func==FUNC_GET_L):
				return FUNC_GET_S
			elif (func==FUNC_SET_L):
				return FUNC_SET_S
		else:
			return func
	def getFunc_L(self):
		func = self.getFunc()
		if (len(func)<=1):
			if (func==FUNC_GET_S):
				return FUNC_GET_L
			elif (func==FUNC_SET_S):
				return FUNC_SET_L
		else:
			return func
	def getParamNum(self):
		return max(0, len(self.textToList())-FIXED_PARAMETERS)
	def getWpar(self):
		return self.getStringInPos(WPAR_POS)
	def getWpar_S(self):
		wpar = self.getWpar()
		if (len(wpar)>1):
			if (wpar==WPAR_TEMP_L):
				return WPAR_TEMP_S
			elif (wpar==WPAR_HUMI_L):
				return WPAR_HUMI_S
		else:
			return wpar
	def getWpar_L(self):
		wpar = self.getWpar()
		if (len(wpar)<=1):
			if (wpar==WPAR_TEMP_S):
				return WPAR_TEMP_L
			elif (wpar==WPAR_HUMI_S):
				return WPAR_HUMI_L
		else:
			return wpar
	def getWparId(self):
		return self.getStringInPos(WPARID_POS)
	def getWparId_S(self):
		wparId = self.getWparId()
		if (len(wparId)>1):
			if (wparId==WPARID_TEMP_LM35_L):
				return WPARID_TEMP_LM35_S
		else:
			return wparId
	def getWparId_L(self):
		wparId = self.getWparId()
		if (len(wparId)<=1):
			if (wparId==WPARID_TEMP_LM35_S):
				return WPARID_TEMP_LM35_L
		else:
			return wparId
	def getValue(self):
		return self.getStringInPos(VALUE_POS)
	# getStringInPos (it checks if we go out of bounds)
	def getStringInPos(self, pos, separator=ACTION_SEPARATOR):
		textFields = self.textToList(separator)
		if (pos >= len(textFields)):
			return ''
		else:
			return textFields[pos]
		
		
		
		
    # ----------------------------------------------------------------------
    # FUNCTIONS
	
	# -----------------------
	# validate()
	def validate(self):
		
		# parameters
		func = self.getFunc()
		type = self.getType()
		
		# ID validate
		if (len(self.getId()) != ID_MAX_SIZE):
			self.validated = False
		# BOARD_ID_TX, BOARD_ID_RX validate
		elif (
		(self.getTxBoardId() != BOARD_ID) and
		(self.getRxBoardId() != BOARD_ID)):
			self.validated = False
		# TYPE validate
		elif (
		(type != TYPE_NORMAL_L) and
		(type != TYPE_TWITTER_L) and
		(type != TYPE_ARDUINO_L) and
		(type != TYPE_NORMAL_S) and
		(type != TYPE_TWITTER_S) and 
		(type != TYPE_ARDUINO_S)):
			self.validated = False
		# FUNC validate
		elif (
		(func != FUNC_GET_L) and
		(func != FUNC_SET_L) and
		(func != FUNC_GET_S) and 
		(func != FUNC_SET_S)):
			self.validated = False
		else:
			self.validated = True
			
		# return self.validate
		return self.validated
	
	
	# -----------------------
	# textToList(self, separator=ACTION_SEPARATOR)
	# split text into a list, respecting that ID field might contain ACTION_SEPARATOR characters
	def textToList(self, separator=ACTION_SEPARATOR):
		return [self.text[:ID_MAX_SIZE]] + self.text[ID_MAX_SIZE+1:].split(ACTION_SEPARATOR)

	
