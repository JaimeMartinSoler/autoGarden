/*
    // ----------------------------------------------------------------------
    // --- rxtx.h                                                         ---
    // ----------------------------------------------------------------------
    // --- High level static functions to deal with RX, TX and also       ---
    // --- generation and execution of received actions                   ---
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-13                                             ---
    // ----------------------------------------------------------------------
*/

#ifndef RXTX_H
#define RXTX_H

#if ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif

// ----------------------------------------------------------------------
// INCLUDES
#include <RF24.h>
#include "action.h"



class RXTX
{
    // ----------------------------------------------------------------------
    // PARAMETERS
    
    // board ID
    public:
      static const String BOARD_ID;
      
    // Generated Actions
    private:
      static const float GA_TEMP_MAX;
      static const unsigned long GA_TEMP_MAX_ACTION_INTERVAL;
      static unsigned long ga_temp_max_action_last;

    // Function Parameters:
    // Function Parameters: Long (length<=4)
    private:
      static const String FUNC_GET_L;
      static const String FUNC_SET_L;
    // Function Parameters: Short (length=1)
    private:
      static const String FUNC_GET_S;
      static const String FUNC_SET_S;
         
    // Weather Parameters:
    // Weather Parameters: Long (length<=4)
    private:
      static const String WPAR_TEMP_L;
      static const String WPAR_HUMI_L;
    // Weather Parameters: Short (length=1)
    private:
      static const String WPAR_TEMP_S;
      static const String WPAR_HUMI_S;
      
    // Sensor Id Parameters:
    // Sensor Id Parameters: Long (length<=4)
    private:
      static const String TEMP_LM35_L;
    // Weather Parameters: Short (length=1)
    private:
      static const String TEMP_LM35_S;
      
    // ----------------------------------------------------------------------
    // FUNCTIONS
    public:
      static bool rx(RF24 &radio, bool rxLoop = false);
      static bool tx(RF24 &radio, Action &action);
      static bool exec(RF24 &radio, Action &action);
    private:
      static bool generateAction(Action &action);
};

#endif

