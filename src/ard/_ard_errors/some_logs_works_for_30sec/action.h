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




class Action
{
    // ----------------------------------------------------------------------
    // PARAMETERS

    // PARAMETERS: STATIC
    
    //ASCII
    private:
      static const short int ASCII_PRINT_MIN;   // '!' first printable ASCII character
      static const short int ASCII_PRINT_MAX;  // '~' last  printable ASCII character
      static const long int ASCII_PRINT_RANGE;
      
    // ID
    public:
      static const short int ID_SIZE; // the number of chars for the ID
      static const long int ID_MAX;   // the maximum int value of the ID
      
    // message size
    private:
      static short int MAX_MESSAGE_SIZE;

    // PARAMETERS: CLASS
    public:
      // Parameters Payload
      String id;            // length=3, any printable ASCII (from #33 to #126)
      String txBoardId;     // length=2, the board id to trasnmit this action message
      String rxBoardId;     // length=2, the board id to receive this action message
      String mode;          // length=1/2: RX/R, TX/T, UN/U, how the RX must behave after action TX
      String title;         // length=3/4, the name of the action 
      short int paramNum;   // param[] size
      String *param;        // any other action parameters
      // Parameters toStr
      String toStr;         // String with the result of this->toString(true)
      // Parameters TX
      bool validated;       // true: paramters are OK; false: parameters NOT_OK
      short int txSuccess;  // number of times this action was successfuly tx
      short int txAttempts; // number of times this action was attampted to be tx
    // ----------------------------------------------------------------------
    // CONSTRUCTORS (they just call the setters)
    public:
      Action();
      Action(Action &action);
      Action(String id, String txBoardId, String rxBoardId, String mode, String title, short int paramNum, String param[], String toStr="", bool validated = false, int txSuccess = 0, int txAttempts = 0, bool forceValidation = true);
      Action(String strAction);
      ~Action();
    // SETTERS
      void set();
      void set(Action &action);
      void set(String id, String txBoardId, String rxBoardId, String mode, String title, short int paramNum, String param[], String toStr="", bool validated = false, int txSuccess = 0, int txAttempts = 0, bool forceValidation = true);
      void set(String strAction);
    // ----------------------------------------------------------------------
    // FUNCTIONS
    public:
      String toString(bool forceGeneration = false);
      String idAdd(int addition);                       // class  version
      static String idAdd(String strId, int addition);  // static version
    private:
      bool validate();
      static long int idToInt(String strId);
      static String intToId(long int intId);
};

#endif

