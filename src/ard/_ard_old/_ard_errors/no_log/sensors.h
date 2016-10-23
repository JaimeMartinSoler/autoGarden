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




class Sensors
{
    // --------------------------------------------------------------
    // PARAMETERS: STATIC

    // NRF24L01: communication
    private:
      static const short int NRF24_PIPE_R;
      static const short int NRF24_PIPE_W;
      static const uint64_t NRF24_PIPES[2];
    public:
      static const short int NRF24_PAYLOAD_MAX_SIZE;      // defined by NRF24 datasheet
      static const short int NRF24_PAYLOAD_ACK_MAX_SIZE;  // defined by NRF24 datasheet
    
    // NRF24L01: pins CE, CSN
    public:
      static const short int NRF24_PIN_CE;
      static const short int NRF24_PIN_CSN;
    
    // LM35: pins
    private:
      static const short int LM35_PIN_ANALOG_IN;


    
  
    // ----------------------------------------------------------------------
    // SETUP FUNCTIONS
    public:
      static void setupAll(RF24 &_radio);
      static void setupNRF24(RF24 &_radio);
      static void setupLM35();
      
    // ----------------------------------------------------------------------
    // FUNCTIONS
    public:
      static float getTempLM35();
};

#endif

