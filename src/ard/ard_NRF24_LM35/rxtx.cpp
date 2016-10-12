/*
    // ----------------------------------------------------------------------
    // --- rxtx.cpp                                                       ---
    // ----------------------------------------------------------------------
    // --- RXTX                                                           ---
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 2016-10-11                                             ---
    // ----------------------------------------------------------------------
*/


// ----------------------------------------------------------------------
// INCLUDES

#include "rxtx.h"
#include "config.h"
#include "action.h"
#include "helper.h"
#include "log.h"
#include <RF24.h>




// ----------------------------------------------------------------------
// FUNCTIONS


// rx()
bool RXTX::rx(RF24 &radio, bool rxLoop = false)
{
  // rx loop (if !rxLoop it breaks at the bottom)
  while(true) {
    
    // RX start listening TX
    radio.startListening();
    
    // RX loop: wait for a message
    LOG(LOG_INF, "\n  RX waiting message...");
    Action txAction;
    while(!radio.available()) {
      // Check sensors to generate actions, if required
      if(generateAction(txAction)) {  // returns true if an action has been generated
        tx(radio, txAction);
        radio.startListening();
      }
      delay(10);
    }
  
    // ACK_TX payload before RX
    // issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
    String strAckTX = "ACK from Arduino";
    char charAckTX[strAckTX.length()];
    strAckTX.toCharArray(charAckTX, strAckTX.length()+1); // TODO: how would this '+1' deal with exact 32 bytes payload???
    radio.writeAckPayload(1, charAckTX, sizeof(charAckTX));
    
    // RX message
    char charMsgRX[MAX_MESSAGE_SIZE];
    radio.read(&charMsgRX, sizeof(charMsgRX));
    String strMsgRX = String(charMsgRX);
    LOG(LOG_INF, "RX: \"" + strMsgRX + "\"");
    LOG(LOG_INF, "  ACK_TX_payload: \"" + strAckTX + "\"");
  
    // create an action from RX and execute it
    Action rxAction(strMsgRX);
    LOG(LOG_INF, "  Action generated: \"" + rxAction.toString() + "\"");
    exec(radio, rxAction);
    LOG(LOG_DEB, "in rx(): exec passed");

    // keep/breake infinite loop
    LOG(LOG_DEB, "in rx(): rxLoop=" + String(rxLoop));
    if (!rxLoop)
      return true;
    LOG(LOG_DEB, "in rx(): last line of loop");
  }
  // if RX loop is broken, return false
  return false;
}


// tx()
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
    LOG(LOG_WAR, "  ACK_RX: NO");
    return false;
    
  // ACK_RX:
  // issue!!!: when a row of msg is read, after TX stops, RX keeps reading ACKs for 2-3 times
  } else {
    action.txSuccess++;
    
    // ACK_RX (ACK payload OK):
    // issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
    if (radio.isAckPayloadAvailable()) {
      char charAckRX[MAX_MESSAGE_SIZE];
      radio.read(&charAckRX, sizeof(charAckRX));
      String strAckRX = String(charAckRX);
      LOG(LOG_INF, "  ACK_RX: YES\n  ACK_RX_payload: \"" + strAckRX + "\"");
      
    // ACK_RX (ACK payload <empty>): 
    } else {
      LOG(LOG_INF, "  ACK_RX: YES\n  ACK_RX_payload: <empty>");
    }
    return true;
  }
  //return true;
}


// exec()
bool RXTX::exec(RF24 &radio, Action &action)
{
  LOG(LOG_INF, "  Action to execute: \"" + action.toString() + "\"");
  
  // check action.validated
  if (!action.validated) {
    LOG(LOG_WAR, "  Action to execute: \"" + action.toString() + "\" is NOT validated");
    return false;
  }

  // RX: "III,TT,<AO>,MM,..."
  if (strEq(action.rxBoardId,BOARD_ID)) {
    
    // "III,TT,<AO>,MM,<GET>,..."
    if (strEq(action.title,"GET")) {
      if (action.paramNum==2) {
        
        // "III,TT,<AO>,MM,<GET>,<T/TEMP>,<0>"
        if((strEq(action.param[0],"T") || strEq(action.param[0],"TEMP")) && strEq(action.param[1],"0")) {
          float tempC = analogRead(PIN_ANALOG_IN_LM35) / 9.31;
          LOG(LOG_INF, "  Action to execute: \"" + action.toString() + "\" successfully executed");
          Action txAction("XYZ," + String(BOARD_ID) + ",R0,UN,SET,TEMP,0,"+String(tempC));
          exec(radio, txAction);
          return true;
        }
      }
    }
  }
  
  // TX: "III,<AO>,RR,MM,..."
  else if (strEq(action.txBoardId,BOARD_ID)) {
    if (tx(radio, action)) {
      LOG(LOG_INF, "  Action to execute: \"" + action.toString() + "\" successfully executed");
      return true;
    }
  }
  
  LOG(LOG_INF, "  Action to execute: \"" + action.toString() + "\" was NOT successfully executed");
  return false;
}


// generateAction()
bool RXTX::generateAction(Action &action)
{
  // Check Temperature
  if (millis() - ga_temp_max_action_last >= GA_TEMP_MAX_ACTION_INTERVAL) {
    // get temperature in celsius [tempF = (tempC * 1.8) + 32]
    float tempC = analogRead(PIN_ANALOG_IN_LM35) / 9.31;
    if (tempC >= GA_TEMP_MAX) {
      ga_temp_max_action_last = millis();
      action.set("000,R0,UN,SET,TEMP,0,"+String(tempC)+",UA");
      LOG(LOG_INF, "Generate Action: tempC >= GA_TEMP_MAX");
      return true;
    }
  }
  // if no action was not generated, return false
  return false;
}


