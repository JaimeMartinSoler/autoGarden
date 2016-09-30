 /*
    // ----------------------------------------------------------------------
    // --- ard_NRF24L01_LM35.ino                                          ---
    // ----------------------------------------------------------------------
    // --- autoGarden main Arduino file, to manage sensors and RPi comm.  ---
    // --- RPi requirements: execute twitter_NRF24L01.py                  ---
    // --- RPi comm.: NRF24L01 2.4GHz wireless transciever                ---
    // --- Sensor: LM35d analog temperature sensor (analog pin 5)         ---
    // --- LM35 ref: http://playground.arduino.cc/Main/LM35HigherResolution -
    // http://www.prometec.net/nrf2401/
    // https://github.com/TMRh20/RF24
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 27/09/2016                                             ---
    // ----------------------------------------------------------------------
*/


// ----------------------------------------------------------------------
// INCLUDES
#include "nRF24L01.h"
#include "RF24.h"
#include "RF24_config.h"
#include <SPI.h>




// ----------------------------------------------------------------------
// PARAMETERS

// PINS
//const int PIN_BROKEN_VCC = 8;   // BROKEN, ALWAYS VCC
const int ANALOG_PIN_IN_LM35 = 5;     

// OTHER PARAMETERS
int msg[1] ;
RF24 radio(9,10);
const uint64_t pipe = 0xE8E8F0F0E1LL;
boolean SERIAL_ON = false;


// ----------------------------------------------------------------------
// SETUP

void setup() {
  
  // LM35 (see LM35 ref: http://playground.arduino.cc/Main/LM35HigherResolution)
  analogReference(INTERNAL);

  // NRF24L01 radio begin and open for writing
  radio.begin();
  radio.openWritingPipe(pipe);
  
  // Serial begin
  if (SERIAL_ON) {Serial.begin(9600);}
}




// ----------------------------------------------------------------------
// MAIN LOOP

void loop() {

  for (int x=0;x<2255;x++)
  {     
    msg[0] = x;
    radio.write(msg, 1);
  }
}


