/*
    // ----------------------------------------------------------------------
    // --- log.cpp                                                        ---
    // ----------------------------------------------------------------------
    // --- General propose og library                                     ---
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-11                                             ---
    // ----------------------------------------------------------------------
*/

// ----------------------------------------------------------------------
// INCLUDES
#include "helper.h"




// ----------------------------------------------------------------------
// FUNCTIONS


// powInt(int base, int exponent)
long int powInt(int base, int exponent)
{
  long int value = 1;
  for (int i=0; i<exponent; i++) {
    value *= base;
  }
  return value;
}


// strEq(String str0, String str1)
bool strEq(String str0, String str1)
{
  return (strcmp(str0.c_str(),str1.c_str()) == 0);
}


