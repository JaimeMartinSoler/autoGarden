/*
    // ----------------------------------------------------------------------
    // --- action.h                                                       ---
    // ----------------------------------------------------------------------
    // --- Actions object, to manage RX/TX messages, meant for NRF24L01   ---
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-10                                             ---
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
// DEFINES --------------------------------------------------------------
//  CONNECTION
#define MAX_MESSAGE_SIZE 32
//  ASCII
#define ASCII_PRINT_MIN 33
#define ASCII_PRINT_MAX 126
const long int ASCII_PRINT_RANGE = ((long int)ASCII_PRINT_MAX - (long int)ASCII_PRINT_MIN + 1); //out of #define bounds
// ID
#define ID_SIZE 3
const long int ID_MAX = (((long int)ASCII_PRINT_RANGE) *((long int)ASCII_PRINT_RANGE) * ((long int)ASCII_PRINT_RANGE) - 1); //out of #define bounds
// BOARD_ID
#define BOARD_ID "A0"


class Action
{
    // ----------------------------------------------------------------------
    // PARAMETERS
    public:
      // Parameters Payload
      String id;            // length=3, any printable ASCII (from #33 to #126)
      String txBoardId;     // length=2, the board id to trasnmit this action message
      String rxBoardId;     // length=2, the board id to receive this action message
      String mode;          // length=1/2: RX/R, TX/T, UN/U, how the RX must behave after action TX
      String title;         // length=3/4, the name of the action 
      short int paramNum;   // param[] size
      String *param;        // any other action parameters
      // Parameters TX
      bool validated;       // true: paramters are OK; false: parameters NOT_OK
      short int txSuccess;  // number of times this action was successfuly tx
      short int txAttempts; // number of times this action was attampted to be tx
    // ----------------------------------------------------------------------
    // CONSTRUCTORS (they just call the setters)
    public:
      Action();
      Action(Action &action);
      Action(String id, String txBoardId, String rxBoardId, String mode, String title, short int paramNum, String param[], bool validate, int txSuccess, int txAttempts, bool forceValidation);
      Action(String strAction);
      ~Action();
    // SETTERS
      void set();
      void set(Action &action);
      void set(String id, String txBoardId, String rxBoardId, String mode, String title, short int paramNum, String param[], bool validate, int txSuccess, int txAttempts, bool forceValidation);
      void set(String strAction);
    // ----------------------------------------------------------------------
    // FUNCTIONS
    public:
      String toString();
      static String idAdd(String strId, int addition);
    private:
      bool validate();
      static long int idToInt(String strId);
      static String intToId(long int intId);
};

#endif

