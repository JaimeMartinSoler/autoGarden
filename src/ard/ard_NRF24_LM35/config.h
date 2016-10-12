/*
    // ----------------------------------------------------------------------
    // --- config.h                                                       ---
    // ----------------------------------------------------------------------
    // --- General propose og library                                     ---
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-11                                             ---
    // ----------------------------------------------------------------------
*/

#ifndef CONFIG_H
#define CONFIG_H

#if ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif


// --------------------------------------------------------------
// PARAMETERS

// 123456789_123456789_123456789_-2-456789_123456789_ - STRING_LENGTH_RULER

// NRF24L01 communication
const short int PIPE_R = 0;
const short int PIPE_W = 1;
const uint64_t pipes[2] = {0xE8E8F0F0E1LL, 0xF0F0F0F0E1LL};
const short int PAYLOAD_MAX_SIZE = 32;      // defined by NRF24 datasheet
const short int PAYLOAD_ACK_MAX_SIZE = 32;  // defined by NRF24 datasheet

// NRF24L01 pins: CE, CSN
const short int PIN_CE = 9;
const short int PIN_CSN = 10;

// LM35 pins and tempC
const short int PIN_ANALOG_IN_LM35 = 5;

#endif

