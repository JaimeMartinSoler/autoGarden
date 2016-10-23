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
      
    // Generated Actions
    private:
      static const float GA_TEMP_MAX;
      static const long GA_TEMP_MAX_ACTION_INTERVAL;
      static long ga_temp_max_action_last;

    // ----------------------------------------------------------------------
    // FUNCTIONS
    public:
      static bool rx(RF24 &radio, bool rxLoop = false);
    private:
      static bool tx(RF24 &radio, Action &action);
      static bool exec(RF24 &radio, Action &action, bool &execActionChanged);
      static bool generateAction(Action &action);
};

#endif

