/*
    // ----------------------------------------------------------------------
    // --- log.h                                                          ---
    // ----------------------------------------------------------------------
    // --- General propose library with helpful functions                 ---
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-11                                             ---
    // ----------------------------------------------------------------------
*/

// ----------------------------------------------------------------------
// INCLUDES
#include "helper.h"




// ----------------------------------------------------------------------
// FUNCTIONS


// powInt(int, int)
// return: base to the power of exponent
long int powInt(int base, int exponent)
{
  long int value = 1;
  for (int i=0; i<exponent; i++) {
    value *= base;
  }
  return value;
}


// strEq(String, String)
// return: true(str0==str1), false(str0!=str1)
bool strEq(String str0, String str1)
{
  return (strcmp(str0.c_str(),str1.c_str()) == 0);
}


