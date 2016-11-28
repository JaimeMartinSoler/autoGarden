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
#include "DHT.h"
#include "sensors.h"
#include "log.h"




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
const bool Sensors::SET_ANALOG_REFERENCE_INTERNAL = false;
const short int Sensors::LM35_PIN_ANALOG_IN = 5;

// DHT22: pins and object
const short int Sensors::DHT_PIN = 2;
const short int Sensors::DHT_TYPE = 22;
// DHT22: object
DHT sensorDHT(Sensors::DHT_PIN, Sensors::DHT_TYPE);

// MH rain drop sensor: pins
const short int Sensors::MH_DIGITAL_PIN = 3;  // pin for threshold input
const short int Sensors::MH_ANALOG_PIN = 4;   // pin for analog input


// ----------------------------------------------------------------------
// SETUP FUNCTIONS

// setupAll(&RF24)
// execute all the sensor setups
void Sensors::setupAll(RF24 &_radio)
{
  Sensors::setupNRF24(_radio);
  Sensors::setupLM35();
  Sensors::setupDHT();
  Sensors::setupMH();
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
  _radio.setDataRate(RF24_1MBPS);    // with RF24_250KBPS: <10% success..., RF24_1MBPS OK
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
  if (SET_ANALOG_REFERENCE_INTERNAL) {
    analogReference(INTERNAL);
  }
}


// setupDHT()
// setupDHT digital temperature sensor
void Sensors::setupDHT()
{
  sensorDHT = DHT(DHT_PIN, DHT_TYPE);
  sensorDHT.begin();
}


// setupMH()
// setupMH rain drop sensor
void Sensors::setupMH()
{
  pinMode(MH_DIGITAL_PIN, INPUT);
}



// ----------------------------------------------------------------------
// FUNCTIONS

// getTempLM35()
// get temperature from LM35 analog temperature sensor
// return: float(temperature in celsius [tempF=(tempC*1.8)+32])
float Sensors::getTempLM35() 
{
  // http://playground.arduino.cc/Main/LM35HigherResolution
  if (SET_ANALOG_REFERENCE_INTERNAL) {
    return analogRead(LM35_PIN_ANALOG_IN) / 9.31;
  } else {
    return analogRead(LM35_PIN_ANALOG_IN) * 500.0 / 1023.0;
  }
}


// getTempDHT()
// get temperature from DHT digital temperature and humidity sensor
// return: float (temperature in celsius [tempF=(tempC*1.8)+32])
float Sensors::getTempDHT() 
{
  return sensorDHT.readTemperature();
}


// getHumiDHT()
// get humidity from DHT digital temperature and humidity sensor
// return: float (humidity as percentage)
float Sensors::getHumiDHT() 
{
  return sensorDHT.readHumidity();
}


// getRainMH(int timeMillis, int periodMillis)
// get rain percentage from MH rain drop sensor, maximum read for timeMillis measured every periodMillis
// return: float (rain drops as percentage)
float Sensors::getRainMH(int timeMillis, int periodMillis) 
// default: (int timeMillis = 1000, int periodMillis = 20)
{
  float rainMH_max = 0.0;
  float rainMH_current = 0.0;
  unsigned long millis_current = millis();
  while((millis() - millis_current) <= (unsigned long)timeMillis) {
    rainMH_current = Sensors::getRainMH_current();
    if (rainMH_current > rainMH_max) {
      rainMH_max = rainMH_current;
    }
    delay(periodMillis);
  }
  return rainMH_max;
}


// getRainMH_current()
// get rain percentage from MH rain drop sensor
// return: float (rain drops as percentage)
float Sensors::getRainMH_current() 
{
  return 100.0 - (((float)analogRead(MH_ANALOG_PIN))*100.0)/1023.0;
}


// getRainMH_digital()
// get rain boolean from the digital output of the MH rain drop sensor
// return: boolean (true if it rains, false otherwise)
bool Sensors::getRainMH_digital() 
{
  // this depends on the manual potenciometer of the MH sensor, currently true if getRainMH() > 30.0% (approx)
  return !(digitalRead(MH_DIGITAL_PIN));
}



