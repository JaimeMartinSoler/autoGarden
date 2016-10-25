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
// CONSTRUCTORS (they just call the setters)

// Constructor: Default
Action::Action(){
  set();
}

// Constructor: Copy
Action::Action(Action &action) {
  set(action);
}

// Constructor: Main
Action::Action(char text[], int textSize){
// defaults: (int textSize = ACTION_MAX_SIZE)
  set(text, textSize);
}

// Constructor: Main String
Action::Action(String str){
  set(str);
}




// ----------------------------------------------------------------------
// SETTERS

// Set: Default
void Action::set() {
  clearAction();
}


// Set: Copy
void Action::set(Action &action) {
  
  clearAction();
  
  // Parameters Payload
  copyCharArray(this->text, action.text, min(sizeof(this->text),sizeof(action.text)));

  // Parameters TX
  this->validated = action.validated;
  this->txSuccess = action.txSuccess;
  this->txAttempts = action.txAttempts;
}


// Set: Main
void Action::set(char text[], int textSize) {
// defaults: (int textSize = ACTION_MAX_SIZE)

  clearAction();
  
  // Parameters Payload
  copyCharArray(this->text, text, textSize);
  
  // Parameters TX
  validate();
  this->txSuccess = 0;
  this->txAttempts = 0;
}


// Set: Main String
void Action::set(String str) {

  // convert String to char array
  int strSize = str.length();
  char textCharArray[ACTION_MAX_SIZE];
  clearCharArray(textCharArray, ACTION_MAX_SIZE);
  stringToCharArray(str, textCharArray, min(strSize, ACTION_MAX_SIZE));
  if (strSize >= ACTION_MAX_SIZE)
    textCharArray[ACTION_MAX_SIZE-1] = '\0';

  // call set(char[])
  set(textCharArray, ACTION_MAX_SIZE);
}


// Destructor
Action::~Action() {
  delete []text;
}




// ----------------------------------------------------------------------
// FUNCTIONS - GETTERS
    
// getId(char[], int)
void Action::getId(char id[], int charArraySize) {
  // default: (int charArraySize = ID_MAX_SIZE)
  getCharArrayInPosition(id, charArraySize, ID_POS);
}
// getTxBoardId(char[], int)
void Action::getTxBoardId(char txBoardId[], int charArraySize) {
  // default: (int charArraySize = BOARD_ID_MAX_SIZE)
  //for (int i=0; i<(charArraySize-1); i++)
  //  txBoardId[i] = 'J';
  //txBoardId[charArraySize-1] = '\0';
  getCharArrayInPosition(txBoardId, charArraySize, BOARD_ID_TX_POS);
  //txBoardId[charArraySize-1] = '\0';
}
// getRxBoardId(char[], int)
void Action::getRxBoardId(char rxBoardId[], int charArraySize) {
  // default: (int charArraySize = BOARD_ID_MAX_SIZE)
  getCharArrayInPosition(rxBoardId, charArraySize, BOARD_ID_RX_POS);
}
// getType(char[], int)
void Action::getType(char mode[], int charArraySize) {
  // default: (int charArraySize = TYPE_MAX_SIZE)
  getCharArrayInPosition(mode, charArraySize, TYPE_POS);
}
// getFunc(char[], int)
void Action::getFunc(char func[], int charArraySize) {
  // default: (int charArraySize = FUNC_MAX_SIZE)
  getCharArrayInPosition(func, charArraySize, FUNC_POS);
}
// getParamNum()
int Action::getParamNum() {
  int separatorsFound = 0;
  for (int i=0; i<ACTION_MAX_SIZE; i++) {
    if (this->text[i] == ACTION_SEPARATOR)
      separatorsFound++;
  }
  return (separatorsFound - FIXED_PARAMETERS + 1);
}
// getWpar(char[], int)
void Action::getWpar(char wpar[], int charArraySize) {
  // default: (int charArraySize = WPAR_MAX_SIZE)
  getCharArrayInPosition(wpar, charArraySize, WPAR_POS);
}
// getWparId(char[], int)
void Action::getWparId(char wparId[], int charArraySize) {
  // default: (int charArraySize = WPARID_MAX_SIZE)
  getCharArrayInPosition(wparId, charArraySize, WPARID_POS);
}
// getValue(char[], int)
void Action::getValue(char value[], int charArraySize) {
  // default: (int charArraySize = VALUE_MAX_SIZE)
  getCharArrayInPosition(value, charArraySize, VALUE_POS);
}




// ----------------------------------------------------------------------
// FUNCTIONS

// clearAction()
void Action::clearAction()
{
  // Parameters Payload
  clearCharArray(this->text, ACTION_MAX_SIZE);
    
  // Parameters TX
  this->validated = false;
  this->txSuccess = 0;
  this->txAttempts = 0;
}


// compareCharArray(char[], char[])
bool Action::compareCharArray(char ca0[], char ca1[], int ca0Size, int ca1Size)
{
  // parameters
  int minSize = min(ca0Size,ca1Size);

  // check ACTION_ANY_CHAR
  if ((ca0Size==1 && ca0[0]==ACTION_ANY_CHAR) || (ca0Size==2 && ca0[0]==ACTION_ANY_CHAR && ca0[1]=='\0'))
    return true;
  if ((ca1Size==1 && ca1[0]==ACTION_ANY_CHAR) || (ca1Size==2 && ca1[0]==ACTION_ANY_CHAR && ca1[1]=='\0'))
    return true;

  // check !=
  for (int i=0; i<minSize; i++) {
    if (ca0[i] != ca1[i]) return false;
  }
  
  // check more characters beyond minSize
  if (ca0Size > ca1Size) {
    if (ca0[minSize] != '\0')
      return false;
  } else if (ca1Size > ca0Size) {
    if (ca1[minSize] != '\0')
      return false;
  }

  // if no char !=, return true
  return true;
}


// idAdd(String, int)
// It gets the String Id result of the sum of the addition plus strId equivalent.
// (i.e.: idAdd("ABC",1)->"ABD", idAdd("ABC",-2)->"ABA")
// It deals with overflow and negative addition.
// return: strId + addition (taking care of type conversions, etc)
String Action::idAdd(String strId, int addition)
{
  long int intId = idToInt(strId);
  if (intId < 0) { return "X";}
  intId += addition;
  if (intId < 0) {
    intId += (ID_MAX+1);
  } else if (intId > ID_MAX) {
    intId -= (ID_MAX+1);
  }
  return intToId(intId);
}




// ----------------------------------------------------------------------
// FUNCTIONS - PRIVATE

// validate()
// it validates (sets validated parameter) depending on the parameters of the Action
// return: true(validated), false(not validated)
bool Action::validate()
{
  // ID parameter
  char id[ID_MAX_SIZE];
  getId(id, ID_MAX_SIZE);
  // BOARD_ID_TX, BOARD_ID_RX parameters
  char txBoardId[BOARD_ID_MAX_SIZE];
  char rxBoardId[BOARD_ID_MAX_SIZE];
  getTxBoardId(txBoardId, BOARD_ID_MAX_SIZE);
  getRxBoardId(rxBoardId, BOARD_ID_MAX_SIZE);
  // TYPE parameters
  char type[TYPE_MAX_SIZE];
  getType(type);
  // FUNC parameters
  char func[FUNC_MAX_SIZE];
  getFunc(func);
  
  // ID validate
  if (charArraySizeUntil0(id,ID_MAX_SIZE) != (ID_MAX_SIZE-1))
    this->validated = false;
  // BOARD_ID_TX, BOARD_ID_RX validate
  else if (!compareCharArray(rxBoardId, BOARD_ID, sizeof(rxBoardId), sizeof(BOARD_ID)) &&
           !compareCharArray(txBoardId, BOARD_ID, sizeof(txBoardId), sizeof(BOARD_ID)))
     this->validated = false;
  // TYPE validate
  else if (!compareCharArray(type, TYPE_NORMAL_L , sizeof(type), sizeof(TYPE_NORMAL_L) ) &&
           !compareCharArray(type, TYPE_TWITTER_L, sizeof(type), sizeof(TYPE_TWITTER_L)) &&
           !compareCharArray(type, TYPE_ARDUINO_L, sizeof(type), sizeof(TYPE_ARDUINO_L)) &&
           !compareCharArray(type, TYPE_NORMAL_S , sizeof(type), sizeof(TYPE_NORMAL_S) ) &&
           !compareCharArray(type, TYPE_TWITTER_S, sizeof(type), sizeof(TYPE_TWITTER_S)) &&
           !compareCharArray(type, TYPE_ARDUINO_S, sizeof(type), sizeof(TYPE_ARDUINO_S)))
    this->validated = false;
  // FUNC validate
  else if (!compareCharArray(func, FUNC_GET_L, sizeof(func), sizeof(FUNC_GET_L)) &&
           !compareCharArray(func, FUNC_SET_L, sizeof(func), sizeof(FUNC_SET_L)) &&
           !compareCharArray(func, FUNC_GET_S, sizeof(func), sizeof(FUNC_GET_S)) &&
           !compareCharArray(func, FUNC_SET_S, sizeof(func), sizeof(FUNC_SET_S)))
    this->validated = false;
  else
    this->validated = true;
    
  // return this->validated;
  return this->validated;
}


// getCharArrayInPosition(char[], int, char)
void Action::getCharArrayInPosition(char charArray[], int charArraySize, int pos, char separator)
// defaults: (char separator = ACTION_SEPARATOR))
{
  // parameters
  char ans[ACTION_MAX_SIZE];
  clearCharArray(ans, ACTION_MAX_SIZE);
  int ansIdx = 0;
  int separatorsFound = 0;
  
  // loop the char array
  for (int i=0; i<ACTION_MAX_SIZE; i++) {
    if ((this->text[i] == ACTION_SEPARATOR) || (this->text[i] == '\0')) {
      if (++separatorsFound > pos)
        break;
    } else if (separatorsFound == pos) {
      ans[ansIdx++] = text[i];
    }
  }

  // check (ansIdx < charArraySize)
  if (ansIdx >= charArraySize) {
    LOG(LOG_WAR, F("<<<WARNING: in Action::getCharArrayInPosition: ansIdx("), String(ansIdx), F(") >= charArraySize("), String(charArraySize), F(")>>>"));
  }
  
  // set the char array
  clearCharArray(charArray, charArraySize);
  copyCharArray(charArray, ans, ansIdx+1); // +1 to copy '\0' termination from ans
}


// idToInt(String)
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
  }
  return intId;
}


// intToId(long int)
// return: it gets the String equivalent to the int intId.
// (i.e.: idToInt(0)->"!!!", idAdd(285888)->"ABC", idAdd(830583)->"~~~")
String Action::intToId(long int intId)
{
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



