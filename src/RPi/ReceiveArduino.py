#!/usr/bin/python

# http://invent.module143.com/daskal_tutorial/rpi-3-tutorial-14-wireless-pi-to-arduino-communication-with-nrf24l01/




# --------------------------------------------------------------
# IMPORTS
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
 



# --------------------------------------------------------------
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

# Message RX
intMsgRx = []
strMsgRx = ''
# Message TX
intMsgTx = []
strMsgTx = ''
# ACK RX
intAckRx = []
strAckRx = ''
# ACK TX
intAckTx = []
strAckTx = ''




# --------------------------------------------------------------
# FUNCTIONS

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
	




# --------------------------------------------------------------
# SETUP

# GPIO as BCM mode as per lib_nrf24 requires
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# NRF24L01 setup
radio = NRF24(GPIO, spidev.SpiDev())
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
radio.setPALevel(NRF24.PA_MIN)
# print details
radio.printDetails()
radio.startListening()
# role
role = ROLE_RX
 

 
 
# --------------------------------------------------------------
# MAIN LOOP

while(True):

	# role == ROLE_RX
	if (role == ROLE_RX):
		radio.startListening()
		
		# wait for a message
		while (not radio.available()):
			time.sleep(0.010)
			
		# ACK_TX payload before RX
		# issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
		strAckTx = 'ACK to Temp from RPi'
		intAckTx = stringToIntArray(strAckTx)
		radio.writeAckPayload(1, intAckTx, len(intAckTx))
		
		# RX the message
		radio.read(intMsgRx, radio.getDynamicPayloadSize())
		strMsgRx = intArrayToString(intMsgRx)
		print("\nRX: \"{}\"".format(strMsgRx))
		print("  ACK_TX_payload: \"{}\"".format(strAckTx))
		
		
	# role == ROLE_TX
	elif (role == ROLE_TX):
		radio.stopListening()
		
		# create message
		strMsgTx = "Hi from Raspberry Pi";
		intMsgTx = stringToIntArray(strMsgTx)
		
		# TX message
		print("\nTX: \"{}\"".format(strMsgTx))
		if(radio.write(intMsgTx) == 0):
			print("  ACK_RX: NO")
		
		# ACK_RX:
		# issue!!!: when a row of msg is read, after TX stops, RX keeps reading ACKs for 2-3 times
		else:
			# ACK_RX (ACK payload OK):
			# issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
			if (radio.isAckPayloadAvailable()):
				radio.read(intAckRx, radio.getDynamicPayloadSize())
				strAckRx = intArrayToString(intAckRx)
				print ("  ACK_RX: YES\n  ACK_RX_payload: \"{}\"".format(strAckRx))
			# ACK_RX (ACK payload <empty>): 
			else:
				print ("  ACK_RX: YES\n  ACK_RX_payload: <empty>")
		# delay
		time.sleep(1)
	
