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
BOARD_ID_MAX_SIZE = 1 # unlike C++, here we do NOT have to include the null char '\0')
BOARD_ID_TX_POS = 1   # position in payload char array
BOARD_ID_RX_POS = 2   # position in payload char array
BOARD_ID ='R'
BOARD_A0_ID = 'A'

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
WPAR_LGHT_L = 'LGHT'
WPAR_RAIN_L = 'RAIN'
# Weather Parameters: Short (length=1)
WPAR_TEMP_S = 'T'
WPAR_HUMI_S = 'H'
WPAR_LGHT_S = 'L'
WPAR_RAIN_S = 'R'

# Sensor Id Parameters
WPARID_MAX_SIZE = 4   # unlike C++, here we do NOT have to include the null char '\0')
WPARID_POS = 6        # position in payload char array
# Sensor Id Parameters: Long (length<=4)
WPARID_TEMP_LM35_L = 'LM35'
WPARID_TEMP_DHT_L = 'DHT'
WPARID_HUMI_DHT_L = 'DHT'
WPARID_LGHT_BH_L = 'BH'
WPARID_RAIN_MH_L = 'MH'
# Weather Parameters: Short (length=1)
WPARID_TEMP_LM35_S = 'L'
WPARID_TEMP_DHT_S = 'D'
WPARID_TEMP_DHT_S = 'D'
WPARID_LGHT_BH_S = 'B'
WPARID_RAIN_MH_S = 'M'

# Value Parameters
VALUE_MAX_SIZE = ACTION_MAX_SIZE  # unlike C++, here we do NOT have to include the null char '\0')
VALUE_POS = 7                     # position in payload char array

# Value2 Parameters
VALUE2_MAX_SIZE = ACTION_MAX_SIZE  # unlike C++, here we do NOT have to include the null char '\0')
VALUE2_POS = 8                     # position in payload char array


	
# ----------------------------------------------------------------------
# FUNCTIONS - STATIC

# -----------------------
# idAdd(String, int)
# It gets the String Id result of the sum of the addition plus strId equivalent.
# (i.e.: idAdd("ABC",1)->"ABD", idAdd("ABC",-2)->"ABA")
# It deals with overflow and negative addition.
# return: strId + addition (taking care of type conversions, etc)
def idAdd(strId, addition):
	if (len(strId) != ID_MAX_SIZE):
		raise ValueError("len(strId)={} != ID_MAX_SIZE={}".format(len(strId),ID_MAX_SIZE))
	return intToId(idToInt(strId) + addition)


# -----------------------
# idToInt(String)
# return: it gets the equivalent int to the String strId.
# (i.e.: idToInt("!!!")->0, idAdd("ABC")->285888, idAdd("~~~")->830583)
def idToInt(strId):
	v = 0
	intId = 0
	if (len(strId) != ID_MAX_SIZE):
		raise ValueError("len(strId)={} != ID_MAX_SIZE={}".format(len(strId),ID_MAX_SIZE))
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
	intId = intId % (ID_MAX+1)
	strId = ''
	divisor = 0
	remain = intId
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
	def getType_L(self):
		type = self.getStringInPos(TYPE_POS)
		if (len(type) >= TYPE_MAX_SIZE):
			return type
		elif (type==TYPE_NORMAL_S):
			return TYPE_NORMAL_L
		elif (type==TYPE_TWITTER_S):
			return TYPE_TWITTER_L
		elif (type==TYPE_ARDUINO_S):
			return TYPE_ARDUINO_L
		else:
			return ''
	def getFunc(self):
		return self.getStringInPos(FUNC_POS)
	def getParamNum(self):
		return max(0, len(self.textToList())-FIXED_PARAMETERS)
	def getWpar(self):
		return self.getStringInPos(WPAR_POS)
	def getWparId(self):
		return self.getStringInPos(WPARID_POS)
	def getValue(self):
		return self.getStringInPos(VALUE_POS)
	def getValue2(self):
		return self.getStringInPos(VALUE2_POS)
	# getStringInPos (it checks if we go out of bounds)
	def getStringInPos(self, pos, separator=ACTION_SEPARATOR):
		textFields = self.textToList(separator)
		if (pos >= len(textFields)):
			return ''
		else:
			return textFields[pos]
		
    # ----------------------------------------------------------------------
    # FUNCTIONS - SETTERS
	def setId(self, id="!!!"):
		if (len(id) != ID_MAX_SIZE):
			raise ValueError("len(id)="+len(id)+" != ID_MAX_SIZE="+ID_MAX_SIZE)
		self.text = id + self.text[ID_MAX_SIZE:]
		
		
		
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


		

# ----------------------------------------------------------------------
# FUNCTIONS STATIC
	
# static getType_S()
def getType_S(p):
	if (len(p) == 1):
		return p
	elif (p==TYPE_NORMAL_L):
		return TYPE_NORMAL_S
	elif (p==TYPE_TWITTER_L):
		return TYPE_TWITTER_S
	elif (p==TYPE_ARDUINO_L):
		return TYPE_ARDUINO_S
	else:
		return ''
# static getType_L()
def getType_L(p):
	if (len(p) > 1):
		return p
	elif (p==TYPE_NORMAL_S):
		return TYPE_NORMAL_L
	elif (p==TYPE_TWITTER_S):
		return TYPE_TWITTER_L
	elif (p==TYPE_ARDUINO_S):
		return TYPE_ARDUINO_L
	else:
		return ''
	
# static getFunc_S()
def getFunc_S(p):
	if (len(p) == 1):
		return p
	elif (p==FUNC_GET_L):
		return FUNC_GET_S
	elif (p==FUNC_SET_L):
		return FUNC_SET_S
	else:
		return ''	
# static getFunc_L()
def getFunc_L(p):
	if (len(p) > 1):
		return p
	elif (p==FUNC_GET_S):
		return FUNC_GET_L
	elif (p==FUNC_SET_S):
		return FUNC_SET_L
	else:
		return ''
	
# static getWpar_S()
def getWpar_S(p):
	if (len(p) == 1):
		return p
	elif (p==WPAR_TEMP_L):
		return WPAR_TEMP_S
	elif (p==WPAR_HUMI_L):
		return WPAR_HUMI_S
	elif (p==WPAR_LGHT_L):
		return WPAR_LGHT_S
	elif (p==WPAR_RAIN_L):
		return WPAR_RAIN_S
	else:
		return ''
# static getWpar_L()
def getWpar_L(p):
	if (len(p) > 1):
		return p
	elif (p==WPAR_TEMP_S):
		return WPAR_TEMP_L
	elif (p==WPAR_HUMI_S):
		return WPAR_HUMI_L
	elif (p==WPAR_LGHT_S):
		return WPAR_LGHT_L
	elif (p==WPAR_RAIN_S):
		return WPAR_RAIN_L
	else:
		return ''
		
# static getWparId_S()
def getWparId_S(p):
	if (len(p) == 1):
		return p
	elif (p==WPARID_TEMP_LM35_L):
		return WPARID_TEMP_LM35_S
	elif (p==WPARID_TEMP_DHT_L):
		return WPARID_TEMP_DHT_S
	elif (p==WPARID_HUMI_DHT_L):
		return WPARID_HUMI_DHT_S
	elif (p==WPARID_LGHT_BH_L):
		return WPARID_LGHT_BH_S
	elif (p==WPARID_RAIN_MH_L):
		return WPARID_RAIN_MH_S
	else:
		return ''
# static getWparId_L()
def getWparId_L(p):
	if (len(p) > 1):
		return p
	elif (p==WPARID_TEMP_LM35_S):
		return WPARID_TEMP_LM35_L
	elif (p==WPARID_TEMP_DHT_S):
		return WPARID_TEMP_DHT_L
	elif (p==WPARID_HUMI_DHT_S):
		return WPARID_HUMI_DHT_L
	elif (p==WPARID_LGHT_BH_S):
		return WPARID_LGHT_BH_L
	elif (p==WPARID_RAIN_MH_S):
		return WPARID_RAIN_MH_L
	else:
		return ''			

		
