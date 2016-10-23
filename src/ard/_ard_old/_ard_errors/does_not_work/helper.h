/*
    // ----------------------------------------------------------------------
    // --- helper.h                                                       ---
    // ----------------------------------------------------------------------
    // --- General propose library with helpful functions                 ---
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-11                                             ---
    // ----------------------------------------------------------------------
*/

#ifndef HELPER_H
#define HELPER_H

#if ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif




// ----------------------------------------------------------------------
// FUNCTIONS

long int powInt(int base, int exponent);
bool strEq(String str0, String str1);

#endif

