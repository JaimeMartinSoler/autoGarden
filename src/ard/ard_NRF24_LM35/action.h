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

// ID
#define ID_MAX_SIZE 4 // including null char '\0'
#define ID_POS 0      // position in payload char array
const short int ID_SIZE = 3;
const long int ID_MAX = (((long int)ASCII_PRINT_RANGE) * ((long int)ASCII_PRINT_RANGE) * ((long int)ASCII_PRINT_RANGE) - 1);

// board ID
#define BOARD_ID_MAX_SIZE 3 // including null char '\0'
#define BOARD_ID_TX_POS 1   // position in payload char array
#define BOARD_ID_RX_POS 2   // position in payload char array
#define BOARD_ID "A0"
#define BOARD_R0_ID "R0"

// mode
#define MODE_MAX_SIZE 3 // including null char '\0'
#define MODE_POS 3      // position in payload char array

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
// Weather Parameters: Short (length=1)
#define WPAR_TEMP_S "T"
#define WPAR_HUMI_S "H"

// Sensor Id Parameters
#define WPARID_MAX_SIZE 5   // including null char '\0'
#define WPARID_POS 6        // position in payload char array
// Sensor Id Parameters: Long (length<=4)
#define WPARID_TEMP_LM35_L "AIR"
// Weather Parameters: Short (length=1)
#define WPARID_TEMP_LM35_S "A"

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
    // SETTERS
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
      void getMode(char mode[], int charArray = MODE_MAX_SIZE);
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
      static String idAdd(String strId, int addition);  // static version
    // ----------------------------------------------------------------------
    // FUNCTIONS - PRIVATE
    private:
      bool validate();
      void getCharArrayInPosition(char charArray[], int charArraySize, int pos, char separator = ACTION_SEPARATOR);
      static long int idToInt(String strId);
      static String intToId(long int intId);
};

#endif

