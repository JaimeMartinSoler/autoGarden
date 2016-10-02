#!/usr/bin/python


    ## ----------------------------------------------------------------------
    ## --- twitter_NRF24L01.py                                            ---
    ## ----------------------------------------------------------------------
    ## --- autoGarden main RPi file, to manage sensors and Arduino comm.  ---
    ## --- Arduino requirements: execute ard_NRF24L01_LM35.ino            ---
    ## --- RPi comm.: NRF24L01 2.4GHz wireless transciever                ---
	## --- tut: http://www.akirasan.net/raspbpi-arduino-com-bidireccional-nrf24l01/
    ## ----------------------------------------------------------------------
    ## --- Author: Jaime Martin Soler                                     ---
    ## --- Date  : 30/09/2016                                             ---
    ## ----------------------------------------------------------------------


# Twython reference:
# https://twython.readthedocs.io/en/latest/index.html
#
# GPIO reference:
# https://sourceforge.net/p/raspberry-gpio-python/wiki/Examples/
#
# Raspberry Pi 3 pins:
# http://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Layout-Model-B-Plus-rotated-2700x900-1024x341.png


# -------------------------------------------------------------------
# IMPORTS
from nrf24 import NRF24
import time

pipes = [[0x65, 0x64, 0x6f, 0x4e, 0x32], [0x65, 0x64, 0x6f, 0x4e, 0x31]]

radio = NRF24()
radio.begin(0, 0, 15, 18) #Set CE and IRQ pins - Edited, original: radio.begin(0, 0, 25, 18)
radio.setRetries(15,15)
radio.setPayloadSize(32)
radio.setChannel(0x4c)	# original: 0x4c

radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MAX)
#radio.setAutoAck(True)
#radio.enableAckPayload()

radio.openReadingPipe(1, pipes[1])
radio.openWritingPipe(pipes[0])

radio.printDetails()
radio.startListening()
radio.powerUp()
cont=0

while True:
  pipe = [0]

  while not radio.available(pipe):
    time.sleep(0.250)

  recv_buffer = []
  radio.read(recv_buffer)
  out = ''.join(chr(i) for i in recv_buffer)
  print out

  cont=cont+1
  print cont
  radio.stopListening()
  if cont==5:
    comando = "ON"
    radio.stopListening()
    print "Envio comando --- ON"
    radio.write(comando)
    radio.startListening()
  if cont==10:
    comando = "OFF"
    radio.stopListening()
    print "Envio comando --- OFF"
    radio.write(comando)
    radio.startListening()
    cont=0
	