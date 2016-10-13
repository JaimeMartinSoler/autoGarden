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

// ----------------------------------------------------------------------
// INCLUDES
#include "log.h"


// ----------------------------------------------------------------------
// FUNCTIONS

// LOG(unsigned short int, String)
// If logLevel>=logText: it prints logText in the serial (with line break ("\n"))
bool LOG(unsigned short int logLevel, String logText) 
{
  if(logLevel >= LOG_LVL) {
    Serial.println(logText);
    #if LOG_FLUSH_ENABLE > 0
      Serial.flush(); // if we don't flush the line, it might crash or many Serial.print calls
    #endif
    #if LOG_DELAY_ENABLE > 0
      delay(LOG_DELAY_ENABLE);
    #endif
    return true;
  } else {
    return false;
  }
}

// LOG_noln(unsigned short int, String)
// If logLevel>=logText: it prints logText in the serial (withOUT line break ("\n"))
bool LOG_noln(unsigned short int logLevel, String logText) 
{
  if(logLevel >= LOG_LVL) {
    Serial.print(logText);
    #if LOG_FLUSH_ENABLE > 0
      Serial.flush(); // if we don't flush the line, it might crash or many Serial.print calls
    #endif
    #if LOG_DELAY_ENABLE > 0
      delay(LOG_DELAY_ENABLE);
    #endif
    return true;
  } else {
    return false;
  }
}


