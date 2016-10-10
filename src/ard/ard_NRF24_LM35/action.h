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
#define ASCII_PRINT_RANGE (ASCII_PRINT_MAX - ASCII_PRINT_MIN + 1)
// ID
#define ID_SIZE 3
#define ID_MAX (ASCII_PRINT_RANGE  *ASCII_PRINT_RANGE * ASCII_PRINT_RANGE - 1)
// BOARD_ID
#define BOARD_ID "A0"


class Action
{
    // ----------------------------------------------------------------------
    // PARAMETERS
    public:
      String id;          // length=3, any printable ASCII (from #33 to #126)
      String boardId;     // length=2, the board id to receive this action message
      String mode;        // length=1/2: RX/R, TX/T, UN/U, how the RX must behave after action TX
      String title;       // length=3/4, the name of the action 
      short int paramNum; // param[] size
      String *param;      // any other action parameters
      bool validated;     // true: paramters are OK; false: parameters NOT_OK
    // ----------------------------------------------------------------------
    // CONSTRUCTORS
    public:
      Action();
      Action(String id, String boardId, String mode, String title, short int paramNum, String param[]);
      Action(String strAction);
      ~Action();
    // ----------------------------------------------------------------------
    // FUNCTIONS
    public:
      bool exec();
      bool tx();
      String toString();
    private:
      bool validate();
      static String idAdd(String strId, int addition);
      static int idToInt(String strId);
      static String intToId(int intId);
      static int powInt(int base, int exponent);
      static bool strEq(String str0, String str1);
};

#endif

