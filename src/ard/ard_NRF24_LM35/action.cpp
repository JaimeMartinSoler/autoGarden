/*
    // ----------------------------------------------------------------------
    // --- action.cpp                                                     ---
    // ----------------------------------------------------------------------
    // --- Actions object, to manage RX/TX messages, meant for NRF24L01   ---
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-10                                             ---
    // ----------------------------------------------------------------------
*/

// ----------------------------------------------------------------------
// INCLUDES
#include "action.h"




// ----------------------------------------------------------------------
// CONSTRUCTORS


// Constructor: Default
Action::Action()
{
  this->id = "";
  this->boardId = "0";
  this->mode = "";
  this->title = "";
  this->paramNum = 0;
  //this->param = null; // error: 'null' was not declared in this scope
  this->validated = false;
}


// Constructor: All Params
Action::Action(String id, String boardId, String mode, String title, short int paramNum, String param[])
{
  this->id = id;
  this->boardId = boardId;
  this->mode = mode;
  this->title = title;
  this->paramNum = paramNum;
  this->param = new String[this->paramNum];
  validate();
}

// Constructor: Main
Action::Action(String strAction)
{
  // get all the fields from strAction (comma separated values)
  const short int maxFieldsSize = 32;
  String fields[maxFieldsSize];
  for (int i=0; i<maxFieldsSize; i++)
    fields[i]="";
  int fieldsSize = 0;
  int charIdx0 = -1;
  int charIdx1 = 0;
  while ((charIdx1 = strAction.indexOf(',',charIdx0+1)) > -1) {
    fields[fieldsSize++] = strAction.substring(charIdx0+1, charIdx1);
    charIdx0 = charIdx1;
  }
  fields[fieldsSize++] = strAction.substring(charIdx0+1, strAction.length());
  
  // fill the paramters
  const int fixedFields = 4;
  this->id = fields[0];
  this->boardId = fields[1];
  this->mode = fields[2];
  this->title = fields[3];
  this->paramNum = fieldsSize - fixedFields;
  if (this->paramNum > 0) {
    this->param = new String[this->paramNum];
    for (int p=0; p<paramNum; p++)
      param[p] = fields[p+fixedFields];
  }

  // validate
  validate();
}


// Destructor
Action::~Action()
{
  delete []param;
}




// ----------------------------------------------------------------------
// FUNCTIONS

// exec()
bool Action::exec()
{
  if (!validated)
    return false;
  if (strEq(title,"GET"))
  {
    // TODO
  }
  return true;
}


// tx()
bool Action::tx()
{
  if (!validated)
    return false;
    
    // TODO
    
  return true;
}


// toString()
String Action::toString()
{
  String str = id + "," + boardId + "," + mode + "," + title;
  for (int i=0; i<paramNum; i++) {
    str += "," + param[i];
  }
  return str;
}


// validate()
bool Action::validate()
{
  int intId = idToInt(id);
  String toStr = toString();
  if (
    (toStr.length() > MAX_MESSAGE_SIZE) ||
    (id.length()!=ID_SIZE) || (intId<0) || (intId>ID_MAX) ||
    (boardId.length() < 1) || (!strEq(boardId,BOARD_ID)) ||
    (mode.length() < 1) ||
    (title.length() < 1) ) {
      validated = false;
  } else {
    validated = true;
  }
  return validated;
}


// idAdd(String strId, int addition)
String Action::idAdd(String strId, int addition)
{
  int intId = idToInt(strId);
  if (intId < 0) { return "X";}
  intId += addition;
  if (intId < 0) {
    intId += (ID_MAX+1);
  } else if (intId > ID_MAX) {
    intId -= (ID_MAX+1);
  }
  return intToId(intId);
}


// idToInt(String strId)
int Action::idToInt(String strId)
{
  int v = 0;
  int intId = 0;
  if (strId.length() != ID_SIZE) {return -1;}
  for(int i=0; i<ID_SIZE; i++) {
    v = (int)strId.charAt(i) - ASCII_PRINT_MIN;
    if ((v < 0) || (v > ASCII_PRINT_RANGE)) { return -1; }
    intId += pow(v, ID_SIZE-i);
  }
  return intId;
}


// intToId(int intId)
String Action::intToId(int intId)
{
  String strId = "";
  int divisor = 0;
  int remain = intId;
  if ((intId < 0) || (intId > ID_MAX)) { return "X"; }
  for (int expon=(ID_SIZE-1); expon>=0; expon--) {
    divisor = powInt(ASCII_PRINT_RANGE,expon);
    strId += String((char)(ASCII_PRINT_MIN+remain/divisor));
    remain = remain%divisor;
  }
  return strId;
}


// powInt(int base, int exponent)
int Action::powInt(int base, int exponent)
{
  int value = 1;
  for (int i=0; i<exponent; i++) {
    value *= value;
  }
  return value;
}


// strEq(String str0, String str1)
bool Action::strEq(String str0, String str1)
{
  return (strcmp(str0.c_str(),str1.c_str()) == 0);
}


