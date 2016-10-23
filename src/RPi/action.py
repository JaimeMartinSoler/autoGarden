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
ID_SIZE = 3
ID_MAX = (ASCII_PRINT_RANGE * ASCII_PRINT_RANGE * ASCII_PRINT_RANGE) - 1

# board ID
BOARD_ID_MAX_SIZE = 2 # unlike C++, here we do NOT have to include the null char '\0')
BOARD_ID_TX_POS = 1   # position in payload char array
BOARD_ID_RX_POS = 2   # position in payload char array
BOARD_ID ='R0'
BOARD_A0_ID = 'A0'

# mode
MODE_MAX_SIZE = 2 # unlike C++, here we do NOT have to include the null char '\0')
MODE_POS = 3      # position in payload char array

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
	if (len(strId) != ID_SIZE):
		return -1
	for i in range(0,ID_SIZE):
		v = ord(strId[i]) - ASCII_PRINT_MIN;
		if ((v < 0) or (v > ASCII_PRINT_RANGE)):
			return -1
		intId += (v * (ASCII_PRINT_RANGE**(ID_SIZE-i-1)))
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
	for expon in range(ID_SIZE-1,-1,-1):
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
	# Parameters TX
	validated = False  	# true: paramters are OK false: parameters NOT_OK
	txSuccess = 0 		# number of times this action was successfuly tx
	txAttempts = 0		# number of times this action was attampted to be tx
	
	
	
	
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
			self.txSuccess = 0
			self.txAttempts = 0
		# Setter Copy: set by actionCopy
		elif (copy != None):
			self.text = copy.text
			self.validated = copy.validated
			self.txSuccess = copy.txSuccess
			self.txAttempts = copy.txAttempts
		# Setter Default:
		else:
			self.text = ''
			self.validated = False
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
	def getMode(self):
		return self.getStringInPos(MODE_POS)
	def getFunc(self):
		return self.getStringInPos(FUNC_POS)
	def getParamNum(self):
		return max(0, len(self.text.split(ACTION_SEPARATOR))-FIXED_PARAMETERS)
	def getWpar(self):
		return self.getStringInPos(WPAR_POS)
	def getWparId(self):
		return self.getStringInPos(WPARID_POS)
	def getValue(self):
		return self.getStringInPos(VALUE_POS)
	# getStringInPos (it checks if we go out of bounds)
	def getStringInPos(self, pos, separator=ACTION_SEPARATOR):
		charArray = self.text.split(ACTION_SEPARATOR)
		if (pos >= len(charArray)):
			return ''
		else:
			return charArray[pos]
		
		
		
		
    # ----------------------------------------------------------------------
    # FUNCTIONS
	
	# -----------------------
	# validate()
	def validate(self):
		
		# FUNC parameter
		func = self.getFunc()
		
		# ID validate
		if (len(self.getId()) != ID_MAX_SIZE):
			self.validated = False
		# BOARD_ID_TX, BOARD_ID_RX validate
		elif (
		(self.getTxBoardId() != BOARD_ID) and
		(self.getRxBoardId() != BOARD_ID)):
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
		