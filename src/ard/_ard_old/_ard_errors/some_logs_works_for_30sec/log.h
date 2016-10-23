/*
    // ----------------------------------------------------------------------
    // --- log.h                                                          ---
    // ----------------------------------------------------------------------
    // --- General propose log library                                    ---
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-13                                             ---
    // ----------------------------------------------------------------------
*/

#ifndef LOG_H
#define LOG_H

#if ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif

// ----------------------------------------------------------------------
// DEFINES

// LOG_LEVEL_X
#define LOG_DEB 0   // debug
#define LOG_DET 1   // detail
#define LOG_INF 2   // info
#define LOG_WAR 3   // warning
#define LOG_ERR 4   // error
#define LOG_CRS 5   // crash
#define LOG_OFI 6   // off_info: Serial.begin(); Serial.println("LOG/Serial is OFF"); Serial.end()
#define LOG_OFF 7   // off

// LOG_LEVEL
#define LOG_LVL LOG_INF                 // the current log level
const long int LOG_BAUDRATE = 115200;   // 9600, 57600, 115200

// Flush and delay
#define LOG_FLUSH_ENABLE 1  // allow Serial.flush(); in every LOG() call
#define LOG_DELAY_ENABLE 0  // 0:no delay, >0: delay(LOG_DELAY_ENABLE); in every LOG() call




// ----------------------------------------------------------------------
// FUNCTIONS

bool LOG_BEGIN(unsigned short int logLevel = LOG_LVL, long int baudRate = LOG_BAUDRATE);
bool LOG(unsigned short int logLevel, String logText);
bool LOG_noln(unsigned short int logLevel, String logText) ;

#endif

