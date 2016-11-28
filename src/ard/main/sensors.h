/*
    // ----------------------------------------------------------------------
    // --- sensors.h                                                      ---
    // ----------------------------------------------------------------------
    // --- High level management of sensors and NRF24L01 setup            ---
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-13                                             ---
    // ----------------------------------------------------------------------
*/


#ifndef SENSORS_H
#define SENSORS_H

#if ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif


// ----------------------------------------------------------------------
// INCLUDES
#include <RF24.h>
#include "DHT.h"




// Class Sensors
class Sensors
{
    // --------------------------------------------------------------
    // PARAMETERS: STATIC
    public:

    // NRF24L01: communication
    static const short int NRF24_PIPE_R;
    static const short int NRF24_PIPE_W;
    static const uint64_t NRF24_PIPES[2];
    static const short int NRF24_PAYLOAD_MAX_SIZE;      // defined by NRF24 datasheet
    static const short int NRF24_PAYLOAD_ACK_MAX_SIZE;  // defined by NRF24 datasheet
    
    // NRF24L01: pins CE, CSN
    static const short int NRF24_PIN_CE;
    static const short int NRF24_PIN_CSN;
    
    // LM35: pins
    // Warning: it increases the resolution for LM35 if set to true, but it will affect to other analog measurements
    static const bool SET_ANALOG_REFERENCE_INTERNAL;
    static const short int LM35_PIN_ANALOG_IN;

    // DHT22: pins
    // DHT sensorDHT(DHT_PIN, DHT_TYPE) declared in sensors.cpp
    static const short int DHT_PIN;
    static const short int DHT_TYPE;

    // MH rain drop sensor: pins
    static const short int MH_DIGITAL_PIN;  // pin for threshold input
    static const short int MH_ANALOG_PIN;   // pin for analog input


    
  
    // ----------------------------------------------------------------------
    // SETUP FUNCTIONS
    public:
      static void setupAll(RF24 &_radio);
      static void setupNRF24(RF24 &_radio);
      static void setupLM35();
      static void setupDHT();
      static void setupMH();
      // TODO
      static void setupBH();
      
    // ----------------------------------------------------------------------
    // FUNCTIONS
    public:
      static float getTempLM35();
      static float getTempDHT();
      static float getHumiDHT();
      static float getRainMH(int timeMillis = 1000, int periodMillis = 20);
      static float getRainMH_current();
      static bool getRainMH_digital();
      // TODO
      static float getLghtBH();
};

#endif

