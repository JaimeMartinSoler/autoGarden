/*
    // ----------------------------------------------------------------------
    // --- ard_NRF24_LM35.h                                               ---
    // ----------------------------------------------------------------------
    // --- Autogarden Arduino main file                                   ---
    // --- Arduino-RaspberryPi high level communication of climate params ---
    // --- NRF24 config:  http://invent.module143.com/daskal_tutorial/rpi-3-tutorial-14-wireless-pi-to-arduino-communication-with-nrf24l01/
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-13                                             ---
    // ----------------------------------------------------------------------
*/




// --------------------------------------------------------------
// INCLUDES
#include <SPI.h>
#include <RF24.h>
#include "config.h"
#include "log.h"
#include "action.h"
#include "rxtx.h"
#include "sensors.h"




// --------------------------------------------------------------
// PARAMETERS
RF24 radioMain(PIN_CE, PIN_CSN);



// --------------------------------------------------------------
// SETUP
void setup(void){
  
  // log/serial setup
  LOG_BEGIN();
  
  // execute all the sensor setups
  Sensors::setupAll(radioMain);

}




// --------------------------------------------------------------
// LOOP
void loop(void){

  // RX loop
  RXTX::rx(radioMain, true);

}



