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
    // config.h: check for sensors pins
  
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

