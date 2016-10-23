/*
    // ----------------------------------------------------------------------
    // --- action.cpp                                                     ---
    // ----------------------------------------------------------------------
    // --- Action objects, to manage RX/TX messages, meant for NRF24L01   ---
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-13                                             ---
    // ----------------------------------------------------------------------
*/


// ----------------------------------------------------------------------
// INCLUDES
#include "action.h"
#include "sensors.h"
#include "rxtx.h"
#include "log.h"
#include "helper.h"


// ----------------------------------------------------------------------
// PARAMETERS: STATIC

// ASCII
const short int Action::ASCII_PRINT_MIN = 33;   // '!' first printable ASCII character
const short int Action::ASCII_PRINT_MAX = 126;  // '~' last  printable ASCII character
const long int Action::ASCII_PRINT_RANGE = ((long int)ASCII_PRINT_MAX - (long int)ASCII_PRINT_MIN + 1);

// ID
const short int Action::ID_SIZE = 3;
const long int Action::ID_MAX = (((long int)ASCII_PRINT_RANGE) *((long int)ASCII_PRINT_RANGE) * ((long int)ASCII_PRINT_RANGE) - 1);

// message size
short int Action::MAX_MESSAGE_SIZE = Sensors::NRF24_PAYLOAD_MAX_SIZE;




// ----------------------------------------------------------------------
// CONSTRUCTORS (they just call the setters)

// Constructor: Default
Action::Action(){
  set();
}

// Constructor: Copy
Action::Action(Action &action) {
  set(action);
}

// Constructor: All Params
Action::Action(String id, String txBoardId, String rxBoardId, String mode, String title, short int paramNum, String param[], String toStr, bool validated, int txSuccess, int txAttempts, bool forceValidation){
// defaults: (String toStr="", bool validated = false, int txSuccess = 0, int txAttempts = 0, bool forceValidation = true)
  set(id, txBoardId, rxBoardId, mode, title, paramNum, param, toStr, validated, txSuccess, txAttempts, forceValidation);
}

// Constructor: Main
Action::Action(String strAction){
  set(strAction);
}




// ----------------------------------------------------------------------
// SETTERS

// Set: Default
void Action::set()
{
  // Parameters Payload
  this->id = "";
  this->txBoardId = "";
  this->rxBoardId = "";
  this->mode = "";
  this->title = "";
  this->paramNum = 0;
  //this->param = null; // error: 'null' was not declared in this scope
    
  // Parameters toStr
  this->toStr = "";
  
  // Parameters TX
  this->validated = false;
  this->txSuccess = 0;
  this->txAttempts = 0;
}


// Set: Copy
void Action::set(Action &action)
{
  // Parameters Payload
  this->id = action.id;
  this->txBoardId = action.txBoardId;
  this->rxBoardId = action.rxBoardId;
  this->mode = action.mode;
  this->title = action.title;
  this->paramNum = action.paramNum;
  this->param = new String[this->paramNum];
  for (int i=0; i<this->paramNum; i++)
    this->param[i] = action.param[i];
    
  // Parameters toStr
  this->toStr = action.toStr;
  
  // Parameters TX
  this->validated = action.validated;
  this->txSuccess = action.txSuccess;
  this->txAttempts = action.txAttempts;
}


// Set: All Params
void Action::set(String id, String txBoardId, String rxBoardId, String mode, String title, short int paramNum, String param[], String toStr, bool validated, int txSuccess, int txAttempts, bool forceValidation)
// // defaults: (String toStr="", bool validated = false, int txSuccess = 0, int txAttempts = 0, bool forceValidation = true)
{
  // Parameters Payload
  this->id = id;
  this->txBoardId = txBoardId;
  this->rxBoardId = rxBoardId;
  this->mode = mode;
  this->title = title;
  this->paramNum = paramNum;
  this->param = new String[this->paramNum];
  for (int i=0; i<this->paramNum; i++)
    this->param[i] = param[i];

  // Parameters toStr
  toString(true); // it sets this->toStr
    
  // Parameters TX
  if (forceValidation)
    validate(); // this manages param validate
  else
    this->validated = validated;
  this->txSuccess = txSuccess;
  this->txAttempts = txAttempts;
}


// Set: Main
void Action::set(String strAction)
{
  // Parameters Payload
  
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
  const int fixedFields = 5;
  this->id = fields[0];
  this->txBoardId = fields[1];
  this->rxBoardId = fields[2];
  this->mode = fields[3];
  this->title = fields[4];
  this->paramNum = fieldsSize - fixedFields;
  if (this->paramNum > 0) {
    this->param = new String[this->paramNum];
    for (int p=0; p<paramNum; p++)
      param[p] = fields[p+fixedFields];
  }

  // Parameters toStr
  toString(true); // it sets this->toStr
  
  // Parameters TX
  validate();
  this->txSuccess = 0;
  this->txAttempts = 0;
}


// Destructor
Action::~Action()
{
  delete []param;
}




// ----------------------------------------------------------------------
// FUNCTIONS


// toString(bool)
// from all the Action parameters, it builds the String meant to be transmitted.
// Note that if we create an Action, and we change manually a paramter,
// that chang would take no effect in toString()=this->toStr, until we call toString(true).
String Action::toString(bool forceGeneration)
// defaults: (bool forceGeneration = false)
{
  // if(forceGeneration): Generate this->toStr from the parameters
  if (forceGeneration) {
    String str = id + "," + txBoardId + "," + rxBoardId + "," + mode + "," + title;
    for (int i=0; i<paramNum; i++) {
      str += "," + param[i];
    }
    this->toStr = str;
  }
  
  // else (and in any case): return the this->toStr parameter
  return this->toStr;
}


// validate()
// it validates (sets validated parameter) depending on the parameters of the Action
// return: true(validated), false(not validated)
bool Action::validate()
{
  long int intId = idToInt(id);
  String toStrText = toString();
  if (
    (toStrText.length() > MAX_MESSAGE_SIZE) ||
    (id.length()!=ID_SIZE) || (intId<0) || (intId>ID_MAX) ||
    (rxBoardId.length() < 1) || (!strEq(txBoardId,RXTX::BOARD_ID) && !strEq(rxBoardId,RXTX::BOARD_ID)) ||
    (mode.length() < 1) ||
    (title.length() < 1) ) {
      LOG(LOG_WAR, "Warning");
      LOG(LOG_WAR, "Warning: Action: \"" + toStrText + "\" not validated");
      validated = false;
  } else {
    validated = true;
  }
  return validated;
}


// idAdd(int)
// non-static version of static idAdd(String, int)
String Action::idAdd(int addition)
{
  this->id = idAdd(this->id, addition);

  // force generate this->toStr
  toString(true);
}


// idAdd(String, int)
// It gets the String Id result of the sum of the addition plus strId equivalent.
// (i.e.: idAdd("ABC",1)->"ABD", idAdd("ABC",-2)->"ABA")
// It deals with overflow and negative addition.
// return: strId + addition (taking care of type conversions, etc)
String Action::idAdd(String strId, int addition)
{
  long int intId = idToInt(strId);
  LOG(LOG_DEB, "intId = " + String(intId));
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
// return: it gets the equivalent int to the String strId.
// (i.e.: idToInt("!!!")->0, idAdd("ABC")->285888, idAdd("~~~")->830583)
long int Action::idToInt(String strId)
{
  int v = 0;
  long int intId = 0;
  if (strId.length() != ID_SIZE) {return -1;}
  for(int i=0; i<ID_SIZE; i++) {
    v = (int)strId.charAt(i) - ASCII_PRINT_MIN;
    if ((v < 0) || (v > ASCII_PRINT_RANGE)) { return -1; }
    intId += (v * powInt(ASCII_PRINT_RANGE, ID_SIZE-i-1));
    //LOG(LOG_DEB, "v * powInt() = " + String(v * powInt(ASCII_PRINT_RANGE, ID_SIZE-i-1)));
  }
  return intId;
}


// intToId(long int)
// return: it gets the String equivalent to the int intId.
// (i.e.: idToInt(0)->"!!!", idAdd(285888)->"ABC", idAdd(830583)->"~~~")
String Action::intToId(long int intId)
{
  // TODO: DEBUG
  String strId = "";
  long int divisor = 0;
  long int remain = intId;
  if ((intId < 0) || (intId > ID_MAX)) { return "X"; }
  for (int expon=(ID_SIZE-1); expon>=0; expon--) {
    divisor = powInt(ASCII_PRINT_RANGE,expon);
    strId += String((char)(ASCII_PRINT_MIN+remain/divisor));
    remain = remain%divisor;
  }
  return strId;
}



