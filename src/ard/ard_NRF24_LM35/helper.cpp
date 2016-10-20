/*
    // ----------------------------------------------------------------------
    // --- helper.cpp                                                     ---
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
#include "log.h"




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


// clearCharArray(char[], short int)
void clearCharArray(char charArray[], short int charArraySize)
{
  for (int i=0; i<charArraySize; i++)
    charArray[i] = '\0';
}


// copyCharArray(char[], char[], short int)
void copyCharArray(char dest[], const char src[], short int minSize)
{
  for (int i=0; i<minSize; i++)
    dest[i] = src[i];
}


// stringToCharArray(String, char[], short int) 
void stringToCharArray(String str, char dest[], short int destSize) 
{
  int strSize = str.length();
  clearCharArray(dest, destSize);
  copyCharArray(dest, str.c_str(), min(destSize, strSize));
}

