/*
    // ----------------------------------------------------------------------
    // --- action.h                                                       ---
    // ----------------------------------------------------------------------
    // --- Action objects, to manage RX/TX messages, meant for NRF24L01   ---
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-13                                             ---
    // ----------------------------------------------------------------------
*/

#ifndef ACTION_H
#define ACTION_H

#if ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif


// ----------------------------------------------------------------------
// INCLUDES
#include "sensors.h"




// ----------------------------------------------------------------------
// DEFINES & CONSTANTS

// separator and max size
#define ACTION_ANY_CHAR '*'
#define ACTION_SEPARATOR ','
#define ACTION_MAX_SIZE 33  // this should be: (Sensors::NRF24_PAYLOAD_MAX_SIZE + 1)
#define FIXED_PARAMETERS 5

// ASCII
const short int ASCII_PRINT_MIN = 33;   // '!' first printable ASCII character
const short int ASCII_PRINT_MAX = 126;  // '~' last  printable ASCII character
const long int ASCII_PRINT_RANGE = ((long int)ASCII_PRINT_MAX - (long int)ASCII_PRINT_MIN + 1);

// Action Tags (see RPi.actionManager.py)
#define ACTION_TYPES_GLOBAL 3
#define ACTION_ARDUINO_ID 2

// ID
#define ID_MAX_SIZE 4 // including null char '\0'
#define ID_POS 0      // position in payload char array
                      // this must be 0, if we change it we would have to change more code,
                      // the reason is that ID admits ',' as value but also is the separator,
                      // so ID is treated specially in some parts of the code in this class
const short int ID_SIZE = ID_MAX_SIZE - 1;  // NOT including null char '\0'
const long int ID_MAX = (((long int)ASCII_PRINT_RANGE) * ((long int)ASCII_PRINT_RANGE) * ((long int)ASCII_PRINT_RANGE) - 1);

// board ID
#define BOARD_ID_MAX_SIZE 2 // including null char '\0'
#define BOARD_ID_TX_POS 1   // position in payload char array
#define BOARD_ID_RX_POS 2   // position in payload char array
#define BOARD_ID "A"
#define BOARD_R0_ID "R"

// Type
#define TYPE_MAX_SIZE 3 // including null char '\0'
#define TYPE_POS 3      // position in payload char array
// Type Parameters: Long (length<=2)
#define TYPE_NORMAL_L "NR"
#define TYPE_TWITTER_L "TW"
#define TYPE_ARDUINO_L "AR"
// Function Parameters: Short (length=1)
#define TYPE_NORMAL_S "N"
#define TYPE_TWITTER_S "T"
#define TYPE_ARDUINO_S "A"

// Function Parameters
#define FUNC_MAX_SIZE 5   // including null char '\0'
#define FUNC_POS 4        // position in payload char array
// Function Parameters: Long (length<=4)
#define FUNC_GET_L "GET"
#define FUNC_SET_L "SET"
// Function Parameters: Short (length=1)
#define FUNC_GET_S "G"
#define FUNC_SET_S "S"
   
// Weather Parameters
#define WPAR_MAX_SIZE 5   // including null char '\0'
#define WPAR_POS 5        // position in payload char array
// Weather Parameters: Long (length<=4)
#define WPAR_TEMP_L "TEMP"
#define WPAR_HUMI_L "HUMI"
#define WPAR_LGHT_L "LGHT"
#define WPAR_RAIN_L "RAIN"
// Weather Parameters: Short (length=1)
#define WPAR_TEMP_S "T"
#define WPAR_HUMI_S "H"
#define WPAR_LGHT_S "L"
#define WPAR_RAIN_S "R"

// Sensor Id Parameters
#define WPARID_MAX_SIZE 5   // including null char '\0'
#define WPARID_POS 6        // position in payload char array
// Sensor Id Parameters: Long (length<=4)
#define WPARID_TEMP_LM35_L "LM35"
#define WPARID_TEMP_DHT_L "DHT"
#define WPARID_HUMI_DHT_L "DHT"
#define WPARID_LGHT_BH_L "BH"
#define WPARID_RAIN_MH_L "MH"
// Weather Parameters: Short (length=1)
#define WPARID_TEMP_LM35_S "L"
#define WPARID_TEMP_DHT_S "D"
#define WPARID_HUMI_DHT_S "D"
#define WPARID_LGHT_BH_S "B"
#define WPARID_RAIN_MH_S "M"

// Value Parameters
#define VALUE_MAX_SIZE ACTION_MAX_SIZE  // including null char '\0'
#define VALUE_POS 7                     // position in payload char array


class Action
{
    // ----------------------------------------------------------------------
    // PARAMETERS

    // PARAMETERS: CLASS
    public:
      // Parameters Payload
      char text[ACTION_MAX_SIZE]; // char array with the action message text
      // Parameters TX
      bool validated;       // true: paramters are OK; false: parameters NOT_OK
      short int txSuccess;  // number of times this action was successfuly tx
      short int txAttempts; // number of times this action was attampted to be tx
    // ----------------------------------------------------------------------
    // CONSTRUCTORS (they just call the setters)
    public:
      Action();
      Action(Action &action);
      Action(char text[], int textSize = ACTION_MAX_SIZE);
      Action(String str);
      ~Action();
    // FUNCTIONS - SETTERS
    public:
      void set();
      void set(Action &action);
      void set(char text[], int textSize = ACTION_MAX_SIZE);
      void set(String str);
    // ----------------------------------------------------------------------
    // FUNCTIONS - GETTERS
    public:
      void getId(char id[], int charArray = ID_MAX_SIZE);
      void getTxBoardId(char txBoardId[], int charArray = BOARD_ID_MAX_SIZE);
      void getRxBoardId(char rxBoardId[], int charArray = BOARD_ID_MAX_SIZE);
      void getType(char type[], int charArray = TYPE_MAX_SIZE);
      void getFunc(char func[], int charArray = FUNC_MAX_SIZE);
      int getParamNum();
      void getWpar(char wpar[], int charArray = WPAR_MAX_SIZE);
      void getWparId(char wparId[], int charArray = WPARID_MAX_SIZE);
      void getValue(char value[], int charArray = VALUE_MAX_SIZE);
    // ----------------------------------------------------------------------
    // FUNCTIONS
    public:
      static bool compareCharArray(char ca0[], char ca1[], int ca0Size, int ca1Size);
      void clearAction();
      static String idAdd(String strId, int addition);
      static long int idToInt(String strId);
      static String intToId(long int intId);
    // ----------------------------------------------------------------------
    // FUNCTIONS - PRIVATE
    private:
      bool validate();
      void getCharArrayInPosition(char charArray[], int charArraySize, int pos, char separator = ACTION_SEPARATOR);
};

#endif

