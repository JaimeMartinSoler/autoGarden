/*
    // ----------------------------------------------------------------------
    // --- rxtx.cpp                                                       ---
    // ----------------------------------------------------------------------
    // --- High level static functions to deal with RX, TX and also       ---
    // --- generation and execution of received actions                   ---
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-13                                             ---
    // ----------------------------------------------------------------------
*/


// ----------------------------------------------------------------------
// INCLUDES

#include <RF24.h>
#include "rxtx.h"
#include "config.h"
#include "log.h"
#include "helper.h"
#include "action.h"
#include "sensors.h"
#include "MemoryFree.h"




// ----------------------------------------------------------------------
// PARAMETERS

// board ID
const String RXTX::BOARD_ID = "A0";

// Generated Actions
const float RXTX::GA_TEMP_MAX = 40.00;
const unsigned long RXTX::GA_TEMP_MAX_ACTION_INTERVAL = 600000;
unsigned long RXTX::ga_temp_max_action_last = 0;

// Function Parameters:
// Function Parameters: Long (length<=4)
const String RXTX::FUNC_GET_L = "GET";
const String RXTX::FUNC_SET_L = "SET";
// Function Parameters: Short (length=1)
const String RXTX::FUNC_GET_S = "G";
const String RXTX::FUNC_SET_S = "S";
   
// Weather Parameters:
// Weather Parameters: Long (length<=4)
const String RXTX::WPAR_TEMP_L = "TEMP";
const String RXTX::WPAR_HUMI_L = "HUMI";
// Weather Parameters: Short (length=1)
const String RXTX::WPAR_TEMP_S = "T";
const String RXTX::WPAR_HUMI_S = "H";

// Sensor Id Parameters:
// Sensor Id Parameters: Long (length<=4)
const String RXTX::TEMP_LM35_L = "AIR";
// Weather Parameters: Short (length=1)
const String RXTX::TEMP_LM35_S = "A";



// ----------------------------------------------------------------------
// FUNCTIONS


// rx(&RF24, rxLoop=false)
// Receive and manage radio message, creating and executing the necessary Actions
// return: true(rx success), false(rx failed)
bool RXTX::rx(RF24 &radio, bool rxLoop)
// defaults: (bool rxLoop = false)
{
  // rx loop (if !rxLoop it breaks at the bottom)
  while(true) {
    
    // RX start listening TX
    radio.startListening();
    
    // RX loop: wait for a message
    LOG(LOG_INF, F("\n  RX waiting message..."));
    LOG(LOG_INF, "      RX1.1: freeMemory()=" + String(freeMemory()));
    Action txAction;
    while(!radio.available()) {
      // Check sensors to generate actions, if required
      if(generateAction(txAction)) {  // returns true if an action has been generated
        tx(radio, txAction);
        radio.startListening();
      }
      delay(10);
    }
    LOG(LOG_INF, "      RX1.2: freeMemory()=" + String(freeMemory()));
  
    // ACK_TX payload before RX
    // issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
    String strAckTX = "ACK from Arduino";
    char charAckTX[strAckTX.length()];
    strAckTX.toCharArray(charAckTX, strAckTX.length()+1); // TODO: how would this '+1' deal with exact 32 bytes payload???
    radio.writeAckPayload(1, charAckTX, sizeof(charAckTX));
    
    // RX message
    char charMsgRX[Sensors::NRF24_PAYLOAD_MAX_SIZE];
    radio.read(&charMsgRX, sizeof(charMsgRX));
    String strMsgRX = String(charMsgRX);
    //LOG(LOG_INF, "RX: \"" + strMsgRX + "\"");
    //LOG(LOG_INF, "  ACK_TX_payload: \"" + strAckTX + "\"");
  
    // create an action from RX and execute it
    Action rxAction(strMsgRX);
    //LOG(LOG_INF, "  Action generated: \"" + rxAction.toString() + "\"");
    LOG(LOG_INF, "      RX2: freeMemory()=" + String(freeMemory()));
    exec(radio, rxAction);
    LOG(LOG_INF, "      RX3: freeMemory()=" + String(freeMemory()));
    //LOG(LOG_DEB, F("in rx(): exec passed"));

    // keep/breake infinite loop
    //LOG(LOG_DEB, "in rx(): rxLoop=" + String(rxLoop));
    if (!rxLoop)
      return true;
    //LOG(LOG_DEB, F("in rx(): last line of loop"));
  }
  // if RX loop is broken, return false
  return false;
}


// tx(&RF24, &Action)
// Transmit the passed Action
// return: true(ACK_RX), false(NO_ACK_RX)
bool RXTX::tx(RF24 &radio, Action &action)
{
  if (!action.validated)
    return false;
    
  // wait a bit for the receiver to get ready for RX mode
  delay(20);
  
  // TX stop listening RX
  radio.stopListening();
    
  // create message
  String strMsgTX = action.toString();
  char charMsgTX[strMsgTX.length()];
  strMsgTX.toCharArray(charMsgTX, strMsgTX.length()+1); // TODO: how would this '+1' deal with exact 32 bytes payload???

  // TX message
  LOG(LOG_INF, "TX: \"" + strMsgTX + "\"");
  
  // No ACK received:
  action.txAttempts++;
  if (!radio.write(&charMsgTX, sizeof(charMsgTX))){
    //LOG(LOG_WAR, F("  ACK_RX: NO"));
    return false;
    
  // ACK_RX:
  // issue!!!: when a row of msg is read, after TX stops, RX keeps reading ACKs for 2-3 times
  } else {
    action.txSuccess++;
    
    // ACK_RX (ACK payload OK):
    // issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
    if (radio.isAckPayloadAvailable()) {
      char charAckRX[Sensors::NRF24_PAYLOAD_MAX_SIZE];
      radio.read(&charAckRX, sizeof(charAckRX));
      String strAckRX = String(charAckRX);
      //LOG(LOG_INF, "  ACK_RX: YES\n  ACK_RX_payload: \"" + strAckRX + "\"");
      
    // ACK_RX (ACK payload <empty>): 
    } else {
      //LOG(LOG_INF, F("  ACK_RX: YES\n  ACK_RX_payload: <empty>"));
    }
    return true;
  }
  //return true;
}


// exec(&RF24,&Action)
// Execute and Action, both received and meant to be transmitted
// return: true(exec success), false(exec failed)
bool RXTX::exec(RF24 &radio, Action &action)
{
  //LOG(LOG_DET, "  Action to execute: \"" + action.toString() + "\"");
  
  // check action.validated
  if (!action.validated) {
    //LOG(LOG_WAR, "  Action to execute: \"" + action.toString() + "\" is NOT validated");
    return false;
  }

// ABC,R0,A0,UN,GET,TEMP,LM35"

  // RX: "III,TT,<AO>,MM,FFF,..."
  //LOG(LOG_DET, "    rxBoardId: \"" + action.rxBoardId + "\"");
  if (strEq(action.rxBoardId,BOARD_ID)) {
    
    // "III,TT,<AO>,MM,<GET>,..."
    //LOG(LOG_DET, "    function: \"" + action.title + "\"");
    if (strEq(action.title,FUNC_GET_L) || strEq(action.title,FUNC_GET_S)) {
      
      // "III,TT,<AO>,MM,<GET>,WWWW,IIII"
      //LOG(LOG_DET, "    paramNum: " + String(action.paramNum));
      if (action.paramNum==2) {
        
        // "III,TT,<AO>,MM,<GET>,<T/TEMP>,IIII"
        //LOG(LOG_DET, "    weather param: \"" + action.param[0] + "\"");
        if(strEq(action.param[0],WPAR_TEMP_L) || strEq(action.param[0],WPAR_TEMP_S)) {
          
          // "III,TT,<AO>,MM,<GET>,<T/TEMP>,<A/AIR>"
          //LOG(LOG_DET, "    weather param id: \"" + action.param[1] + "\"");
          if(strEq(action.param[1],TEMP_LM35_L) || strEq(action.param[1],TEMP_LM35_S)) {
            float tempC = Sensors::getTempLM35();
            //LOG(LOG_INF, "  Action to execute: \"" + action.toString() + "\" successfully executed");
            LOG(LOG_INF, "      EX1: freeMemory()=" + String(freeMemory()));
            Action txAction("XYZ," + BOARD_ID + ",R0,UN,SET,TEMP,AIR," + String(tempC));
            LOG(LOG_INF, "      EX2: freeMemory()=" + String(freeMemory()));
            //LOG(LOG_DET, "    txAction.validated: \"" + String(txAction.validated) + "\"");
            exec(radio, txAction);
            return true;
          }
        }
      }
    }
  }
  
  // TX: "III,<AO>,RR,MM,..."
  else if (strEq(action.txBoardId,BOARD_ID)) {
    if (tx(radio, action)) {
      //LOG(LOG_INF, "  Action to execute: \"" + action.toString() + "\" successfully executed");
      return true;
    }
  }
  
  //LOG(LOG_WAR, "  Action to execute: \"" + action.toString() + "\" was NOT successfully executed");
  return false;
}


// generateAction(&Action)
// Checks the status of the sensors and autonomously generates and Action, if needed
// This function is meant to be executed in the RX wait loop every few milliseconds
// return: true(action generated), false(no action generated)
bool RXTX::generateAction(Action &action)
{
  // Check Temperature
  if (millis() - ga_temp_max_action_last >= GA_TEMP_MAX_ACTION_INTERVAL) {
    // get temperature in celsius
    float tempC = Sensors::getTempLM35();
    if (tempC >= GA_TEMP_MAX) {
      ga_temp_max_action_last = millis();
      action.set("000,R0,UN,SET,TEMP,0,"+String(tempC)+",UA");
      //LOG(LOG_INF, F("Generate Action: tempC >= GA_TEMP_MAX"));
      return true;
    }
  }
  // if no action was not generated, return false
  return false;
}


