/*
    // ----------------------------------------------------------------------
    // --- sensors.cpp                                                    ---
    // ----------------------------------------------------------------------
    // --- High level management of sensors and NRF24L01 setup            ---
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-13                                             ---
    // ----------------------------------------------------------------------
*/


// ----------------------------------------------------------------------
// INCLUDES
#include <RF24.h>
#include "config.h"
#include "sensors.h"




// --------------------------------------------------------------
// PARAMETERS

// NRF24L01: communication
const short int Sensors::NRF24_PIPE_R = 0;
const short int Sensors::NRF24_PIPE_W = 1;
const uint64_t Sensors::NRF24_PIPES[2] = {0xE8E8F0F0E1LL, 0xF0F0F0F0E1LL};
const short int Sensors::NRF24_PAYLOAD_MAX_SIZE = 32;      // defined by NRF24 datasheet
const short int Sensors::NRF24_PAYLOAD_ACK_MAX_SIZE = 32;  // defined by NRF24 datasheet

// NRF24L01: pins CE, CSN
const short int Sensors::NRF24_PIN_CE = 9;
const short int Sensors::NRF24_PIN_CSN = 10;

// LM35: pins
const short int Sensors::LM35_PIN_ANALOG_IN = 5;




// ----------------------------------------------------------------------
// SETUP FUNCTIONS

// setupAll(&RF24)
// execute all the sensor setups
void Sensors::setupAll(RF24 &_radio)
{
  Sensors::setupNRF24(_radio);
  Sensors::setupLM35();
}


// setupNRF24(&RF24) 
// setup NRF24L01 wireless 2.4GHz transciever
void Sensors::setupNRF24(RF24 &_radio) 
{
  // begin setup
  _radio.begin();
  
  // message and ACK
  _radio.setPayloadSize(NRF24_PAYLOAD_MAX_SIZE);
  _radio.enableDynamicPayloads();    // instead of: radioMain.setPayloadSize(int);
  _radio.setAutoAck(true);
  _radio.enableAckPayload();
  _radio.setRetries(1,15);           // min 1/4_of_ms between retries, max number of retries
  
  // channel and NRF24_PIPES
  _radio.setChannel(0x76);
  _radio.openReadingPipe(1, NRF24_PIPES[NRF24_PIPE_R]);
  _radio.openWritingPipe(NRF24_PIPES[NRF24_PIPE_W]);
  
  // rate, power
  _radio.setDataRate(RF24_1MBPS);    // with RF24_250KBPS: <10% success...
  _radio.setPALevel(RF24_PA_HIGH);
  //_radio.powerUp();
  
  // print details (printf_begin();)
  //_radio.printDetails();
}


// setupLM35()
// setup LM35 analog temperature sensor
void Sensors::setupLM35()
{
  // LM35 setup (see LM35 ref: http://playground.arduino.cc/Main/LM35HigherResolution)
  analogReference(INTERNAL);
}




// ----------------------------------------------------------------------
// FUNCTIONS

// getTempLM35()
// get temperature from LM35 analog temperature sensor
// return: float(temperature in celsius)
float Sensors::getTempLM35() 
{
  // get temperature in celsius [tempF = (tempC * 1.8) + 32]
  return analogRead(LM35_PIN_ANALOG_IN) / 9.31;
}


