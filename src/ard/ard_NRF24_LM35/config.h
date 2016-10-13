/*
    // ----------------------------------------------------------------------
    // --- config.h                                                       ---
    // ----------------------------------------------------------------------
    // --- Configuration library for global variables                     ---
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


// STRING_LENG
// 123456789_123456789_123456789_-2-456789_123456789_

// --------------------------------------------------------------
// LOGS
// see log.h


// --------------------------------------------------------------
// NRF24L01

// NRF24L01 communication
const short int PIPE_R = 0;
const short int PIPE_W = 1;
const uint64_t pipes[2] = {0xE8E8F0F0E1LL, 0xF0F0F0F0E1LL};
const short int PAYLOAD_MAX_SIZE = 32;      // defined by NRF24 datasheet
const short int PAYLOAD_ACK_MAX_SIZE = 32;  // defined by NRF24 datasheet

// NRF24L01 pins: CE, CSN
const short int PIN_CE = 9;
const short int PIN_CSN = 10;


// --------------------------------------------------------------
// SENSORS

// LM35 pins and tempC
const short int PIN_ANALOG_IN_LM35 = 5;


// --------------------------------------------------------------
// ACTION

// ACTION: ASCII
const short int ASCII_PRINT_MIN = 33;   // '!' first printable ASCII character
const short int ASCII_PRINT_MAX = 126;  // '~' last  printable ASCII character
const long int ASCII_PRINT_RANGE = ((long int)ASCII_PRINT_MAX - (long int)ASCII_PRINT_MIN + 1);

// ACTION: ID
const short int ID_SIZE = 3;
const long int ID_MAX = (((long int)ASCII_PRINT_RANGE) *((long int)ASCII_PRINT_RANGE) * ((long int)ASCII_PRINT_RANGE) - 1);

// ACTION: BOARD_ID
const String BOARD_ID = "A0";

#endif

