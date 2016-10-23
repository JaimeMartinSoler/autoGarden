/*
    // ----------------------------------------------------------------------
    // --- log.cpp                                                        ---
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
#include "MemoryFree.h"


// ----------------------------------------------------------------------
// FUNCTIONS

// LOG_BEGIN(long int)
bool LOG_BEGIN(unsigned short int logLevel, long int baudRate)
// defaults: (unsigned short int logLevel = LOG_LVL, long int baudRate = LOG_BAUDRATE)
{
  if ((logLevel < LOG_OFF) && (baudRate > 0))
    Serial.begin(baudRate);
}


// LOG(unsigned short int, String)
// If logLevel>=logText: it prints logText in the serial (with line break ("\n"))
bool LOG(unsigned short int logLevel, String str0, String str1, String str2, String str3, String str4)
// defaults: (String str1 = "", String str2 = "", String str3 = "", String str4 = "")
{
  if(logLevel >= LOG_LVL) {
    
    if (str1.length() == 0) {
      Serial.println(str0);
    } else {
      Serial.print(str0);
      if (str2.length() == 0) {
        Serial.println(str1);
      } else {
        Serial.print(str1);
        if (str3.length() == 0) {
          Serial.println(str2);
        } else {
          Serial.print(str2);
          if (str4.length() == 0) {
            Serial.println(str3);
          } else {
            Serial.print(str3);
            Serial.println(str4);
    } } } }
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
bool LOG_noln(unsigned short int logLevel, String str0, String str1, String str2, String str3, String str4)
// defaults: (String str1 = "", String str2 = "", String str3 = "", String str4 = "")
{
  if(logLevel >= LOG_LVL) {
    Serial.print(str0);
    if (str1.length() > 0) {
      Serial.print(str1);
      if (str2.length() > 0) {
        Serial.print(str2);
        if (str3.length() > 0) {
          Serial.print(str3);
          if (str4.length() > 0) {
            Serial.print(str4);
    } } } }
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


// LOG_FreeMemory() 
// It prints the free memory if it is <LOG_MIN_MEMORY_WARNING, or alway when LOG_MIN_MEMORY_WARNING=0
void LOG_FreeMemory() 
{
  int freeMem = freeMemory();
  #if LOG_MIN_MEMORY_WARNING > 0
    if (freeMem < LOG_MIN_MEMORY_WARNING) {
      LOG_noln(LOG_WAR, F("<<<WARNING: Free Memory = "));
      LOG_noln(LOG_WAR, String(freeMem));
      LOG(LOG_WAR, F(" bytes>>>"));
    }
  #else
    LOG_noln(LOG_INF, F("    Free Memory = "));
    LOG_noln(LOG_INF, String(freeMem);
    LOG(LOG_INF, F(" bytes"));
  #endif
}

