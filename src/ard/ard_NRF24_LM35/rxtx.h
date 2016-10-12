/*
    // ----------------------------------------------------------------------
    // --- rxtx.h                                                         ---
    // ----------------------------------------------------------------------
    // --- TODO                                                           ---
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-11                                             ---
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
#include "action.h"
#include <RF24.h>


// ----------------------------------------------------------------------
// PARAMETERS
// Generated Actions
const float GA_TEMP_MAX = 40.00;
const unsigned long GA_TEMP_MAX_ACTION_INTERVAL = 600000;
static unsigned long ga_temp_max_action_last = 0; // initialized to 0 in .cpp


class RXTX
{
    // ----------------------------------------------------------------------
    // FUNCTIONS
    public:
      static bool rx(RF24 &radio, bool rxLoop);
      static bool tx(RF24 &radio, Action &action);
      static bool exec(RF24 &radio, Action &action);
    private:
      static bool generateAction(Action &action);
};

#endif

