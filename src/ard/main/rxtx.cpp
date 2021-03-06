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
#include "log.h"
#include "helper.h"
#include "action.h"
#include "sensors.h"
#include "MemoryFree.h"




// ----------------------------------------------------------------------
// PARAMETERS

// Generated Actions
const float RXTX::GA_TEMP_MAX = 26.00;
const long RXTX::GA_TEMP_MAX_ACTION_INTERVAL = 600000;
long RXTX::ga_temp_max_action_last = -RXTX::GA_TEMP_MAX_ACTION_INTERVAL;




// ----------------------------------------------------------------------
// FUNCTIONS


// rx(&RF24, rxLoop=false)
// Receive and manage radio message, creating and executing the necessary Actions
// return: true(rx success), false(rx failed)
bool RXTX::rx(RF24 &radio, bool rxLoop)
// defaults: (bool rxLoop = false)
{
  Action rxAction, txAction;
  
  // rx loop (if !rxLoop it breaks at the bottom)
  while(true) {
    
    LOG_FreeMemory();
    
    // RX start listening TX
    radio.startListening();
    
    // RX loop: wait for a message
    LOG(LOG_INF, F("\n  RX waiting message..."));
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
    char charAckTX[] = "ACK from Arduino";
    radio.writeAckPayload(1, charAckTX, sizeof(charAckTX));
    
    // RX message
    char charMsgRX[Sensors::NRF24_PAYLOAD_MAX_SIZE];
    radio.read(&charMsgRX, sizeof(charMsgRX));
    LOG(LOG_INF, F("RX: \""), String(charMsgRX), F("\""));
    LOG(LOG_INF, F("  ACK_TX_payload: \""), String(charAckTX), F("\""));
  
    // create an action from RX and execute it
    rxAction.set(charMsgRX);
    LOG(LOG_DET, F("  Action generated: \""), String(rxAction.text), F("\""));
    // issue!!!: Arduino shows memory problems with heavy recursion, so with this loop we avoid recursion
    // but exec can still update the action to execute, although exec cannot call >1 exec at once
    bool execActionChanged = true;
    while (execActionChanged) {
      exec(radio, rxAction, execActionChanged);
    }

    // keep/breake infinite loop
    if (!rxLoop)
      return true;
    
    LOG_FreeMemory();
  }
  // if RX loop is broken, return false
  return false;
}


// tx(&RF24, &Action)
// Transmit the passed Action
// return: true(ACK_RX), false(NO_ACK_RX)
bool RXTX::tx(RF24 &radio, Action &action)
{
  if (!action.validated) {
    LOG(LOG_WAR, F("<<< WARNING: Action NOT TX, Action NOT Validated >>>"));
    return false;
  }
    
  // wait a bit for the receiver to get ready for RX mode
  delay(20);
  
  // TX stop listening RX
  radio.stopListening();
    
  // create message
  char charMsgTX[Sensors::NRF24_PAYLOAD_MAX_SIZE];
  copyCharArray(charMsgTX, action.text, min(sizeof(charMsgTX),sizeof(action.text)));
  // TX message
  LOG(LOG_INF, F("TX: \""), String(charMsgTX), F("\""));
  
  // No ACK received:
  action.txAttempts++;
  if (!radio.write(&charMsgTX, min(Sensors::NRF24_PAYLOAD_MAX_SIZE,sizeof(charMsgTX)-1))){  // -1, to prevent '\0' from tx
    LOG(LOG_WAR, F("<<< WARNING:  ACK_RX: NOT received >>>"));
    return false;
  }
  // ACK_RX:
  // issue!!!: when a row of msg is read, after TX stops, RX keeps reading ACKs for 2-3 times
  else {
    action.txSuccess++;
    
    // ACK_RX (ACK payload OK):
    // issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
    if (radio.isAckPayloadAvailable()) {
      char charAckRX[Sensors::NRF24_PAYLOAD_ACK_MAX_SIZE];
      radio.read(&charAckRX, sizeof(charAckRX));
      LOG(LOG_INF, F("  ACK_RX: YES (ack_payload=\""), String(charAckRX), F("\")"));
    } 
    // ACK_RX (ACK payload <empty>): 
    else {
      LOG(LOG_INF, F("  ACK_RX: YES (ack_payload=<empty>)"));
    }
    return true;
  }
  //return true;
}


// exec(&RF24,&Action,&bool)
// Execute and Action, both received and meant to be transmitted
// return: true(exec success), false(exec failed)
bool RXTX::exec(RF24 &radio, Action &action, bool &execActionChanged)
{
  LOG(LOG_INF, F("  Action to execute: \""), String(action.text), F("\""));

  execActionChanged = false;
  
  // check action.validated
  if (!action.validated) {
    LOG(LOG_WAR, F("  Action to execute: \""), String(action.text), F("\" is NOT validated"));
    return false;
  }

  // get all parameters: char arrays declarations
  char id[ID_MAX_SIZE];
  char txBoardId[BOARD_ID_MAX_SIZE];
  char rxBoardId[BOARD_ID_MAX_SIZE];
  char type[TYPE_MAX_SIZE];
  char func[FUNC_MAX_SIZE];
  int paramNum;
  char wpar[WPAR_MAX_SIZE];
  char wparId[WPARID_MAX_SIZE];
  char value[VALUE_MAX_SIZE];
  char value2[VALUE2_MAX_SIZE];
  
  // get all parameters: char arrays initialization
  action.getId(id);
  action.getTxBoardId(txBoardId);
  action.getRxBoardId(rxBoardId);
  action.getType(type);
  action.getFunc(func);
  paramNum = action.getParamNum();
  action.getWpar(wpar);
  action.getWparId(wparId);
  action.getValue(value);
  action.getValue2(value2);
  
  // get all parameters: logs
  LOG(LOG_DET, F("    ID: \""), String(id), F("\""));
  LOG(LOG_DET, F("    txBoardId: \""), String(txBoardId), F("\""));
  LOG(LOG_DET, F("    rxBoardId: \""), String(rxBoardId), F("\""));
  LOG(LOG_DET, F("    type: \""), String(type), F("\""));
  LOG(LOG_DET, F("    function: \""), String(func), F("\""));
  LOG(LOG_DET, F("    paramNum: "), String(paramNum));
  LOG(LOG_DET, F("    weather param: \""), String(wpar), F("\""));
  LOG(LOG_DET, F("    weather param id: \""), String(wparId), F("\""));
  LOG(LOG_DET, F("    value: \""), String(value), F("\""));
  LOG(LOG_DET, F("    value2: \""), String(value2), F("\""));

  // BOARD_ID = RX
  if (Action::compareCharArray(rxBoardId, BOARD_ID, sizeof(rxBoardId), sizeof(BOARD_ID))) {
    
    // FUNC = GET
    if (Action::compareCharArray(func,FUNC_GET_L, sizeof(func), sizeof(FUNC_GET_L)) ||
        Action::compareCharArray(func,FUNC_GET_S, sizeof(func), sizeof(FUNC_GET_S))) {
      
      // paramNum >= 2
      if (paramNum>=2) {
        
        // WPAR = TEMP
        if (Action::compareCharArray(wpar, WPAR_TEMP_L, sizeof(wpar), sizeof(WPAR_TEMP_L)) ||
            Action::compareCharArray(wpar, WPAR_TEMP_S, sizeof(wpar), sizeof(WPAR_TEMP_S))) {
          
          // WPARID = LM35
          if (Action::compareCharArray(wparId, WPARID_TEMP_LM35_L, sizeof(wparId), sizeof(WPARID_TEMP_LM35_L)) ||
              Action::compareCharArray(wparId, WPARID_TEMP_LM35_S, sizeof(wparId), sizeof(WPARID_TEMP_LM35_S))) {
            float tempLM35 = Sensors::getTempLM35();
            LOG(LOG_DET, F("  Action to execute: \""), String(action.text), F("\" successfully executed"));
            action.set(
              Action::idAdd(String(id),ACTION_TYPES_GLOBAL) + F(",") +
              String(BOARD_ID) + F(",") +
              String(BOARD_R0_ID) + F(",") +
              String(type) + F(",") +
              String(FUNC_SET_S) + F(",") +
              String(WPAR_TEMP_L) + F(",") +
              String(WPARID_TEMP_LM35_L) + F(",") +
              String(tempLM35)
            );
            execActionChanged = true;
            return true;
          }
          
          // WPARID = DHT (for WPAR = TEMP)
          else if (Action::compareCharArray(wparId, WPARID_TEMP_DHT_L, sizeof(wparId), sizeof(WPARID_TEMP_DHT_L)) ||
                   Action::compareCharArray(wparId, WPARID_TEMP_DHT_S, sizeof(wparId), sizeof(WPARID_TEMP_DHT_S))) {
            float tempDHT = Sensors::getTempDHT();
            LOG(LOG_DET, F("  Action to execute: \""), String(action.text), F("\" successfully executed"));
            action.set(
              Action::idAdd(String(id),ACTION_TYPES_GLOBAL) + F(",") +
              String(BOARD_ID) + F(",") +
              String(BOARD_R0_ID) + F(",") +
              String(type) + F(",") +
              String(FUNC_SET_S) + F(",") +
              String(WPAR_TEMP_L) + F(",") +
              String(WPARID_TEMP_DHT_L) + F(",") +
              String(tempDHT)
            );
            execActionChanged = true;
            return true;
          }
        } 
        
        // WPAR = HUMI
        else if (Action::compareCharArray(wpar, WPAR_HUMI_L, sizeof(wpar), sizeof(WPAR_HUMI_L)) ||
                 Action::compareCharArray(wpar, WPAR_HUMI_S, sizeof(wpar), sizeof(WPAR_HUMI_S))) {

          // WPARID = DHT (for WPAR = HUMI)
          if (Action::compareCharArray(wparId, WPARID_HUMI_DHT_L, sizeof(wparId), sizeof(WPARID_HUMI_DHT_L)) ||
              Action::compareCharArray(wparId, WPARID_HUMI_DHT_S, sizeof(wparId), sizeof(WPARID_HUMI_DHT_S))) {
            float humiDHT = Sensors::getHumiDHT();
            LOG(LOG_DET, F("  Action to execute: \""), String(action.text), F("\" successfully executed"));
            action.set(
              Action::idAdd(String(id),ACTION_TYPES_GLOBAL) + F(",") +
              String(BOARD_ID) + F(",") +
              String(BOARD_R0_ID) + F(",") +
              String(type) + F(",") +
              String(FUNC_SET_S) + F(",") +
              String(WPAR_HUMI_L) + F(",") +
              String(WPARID_HUMI_DHT_L) + F(",") +
              String(humiDHT)
            );
            execActionChanged = true;
            return true;
          }
        }
        
        // WPAR = RAIN
        else if (Action::compareCharArray(wpar, WPAR_RAIN_L, sizeof(wpar), sizeof(WPAR_RAIN_L)) ||
                 Action::compareCharArray(wpar, WPAR_RAIN_S, sizeof(wpar), sizeof(WPAR_RAIN_S))) {
                  
          // WPARID = MH
          if (Action::compareCharArray(wparId, WPARID_RAIN_MH_L, sizeof(wparId), sizeof(WPARID_RAIN_MH_L)) ||
              Action::compareCharArray(wparId, WPARID_RAIN_MH_S, sizeof(wparId), sizeof(WPARID_RAIN_MH_S))) {
            float rainMH = 0.0;
            // NO VALUE
            if (paramNum==2) {
              rainMH = Sensors::getRainMH();
            // VALUE = rainMH time
            } else if (paramNum==3) {
              rainMH = Sensors::getRainMH(String(value).toInt());
            // VALUE2 = rainMH period
            } else if (paramNum>=4) {
              rainMH = Sensors::getRainMH(String(value).toInt(),String(value2).toInt());
            }
            LOG(LOG_DET, F("  Action to execute: \""), String(action.text), F("\" successfully executed"));
            action.set(
              Action::idAdd(String(id),ACTION_TYPES_GLOBAL) + F(",") +
              String(BOARD_ID) + F(",") +
              String(BOARD_R0_ID) + F(",") +
              String(type) + F(",") +
              String(FUNC_SET_S) + F(",") +
              String(WPAR_RAIN_L) + F(",") +
              String(WPARID_RAIN_MH_L) + F(",") +
              String(rainMH)
            );
            execActionChanged = true;
            return true;
          }
        }
      }
    }
  }
  
  // BOARD_ID = TX
  else if (Action::compareCharArray(txBoardId, BOARD_ID, sizeof(txBoardId), sizeof(BOARD_ID))) {
    tx(radio, action);
    radio.startListening();
    if (action.txSuccess>0) {
      LOG(LOG_DET, F("  Action to execute: \""), String(action.text), F("\" successfully executed"));
      return true;
    }
  }
  
  LOG(LOG_WAR, F("<<< WARNING: Action to execute: \""), String(action.text), F("\" was NOT successfully executed >>>"));
  return false;
}


// generateAction(&Action)
// Checks the status of the sensors and autonomously generates and Action, if needed
// This function is meant to be executed in the RX wait loop every few milliseconds
// return: true(action generated), false(no action generated)
bool RXTX::generateAction(Action &action)
{
  // initial id parameter
  static long int txID = ACTION_ARDUINO_ID + ACTION_TYPES_GLOBAL;
  // Check Temperature
  if ((signed long)millis() - ga_temp_max_action_last >= GA_TEMP_MAX_ACTION_INTERVAL) {
    // get temperature in celsius
    float tempDHT = Sensors::getTempDHT();
    if (tempDHT >= GA_TEMP_MAX) {
      ga_temp_max_action_last = (signed long)millis();
      action.set(
        Action::intToId(txID) + F(",") +
        String(BOARD_ID) + F(",") +
        String(BOARD_R0_ID) + F(",") +
        String(TYPE_ARDUINO_S) + F(",") +
        String(FUNC_SET_S) + F(",") +
        String(WPAR_TEMP_L) + F(",") +
        String(WPARID_TEMP_DHT_L) + F(",") +
        String(tempDHT)
      );
      txID += (ACTION_TYPES_GLOBAL*2);
      LOG(LOG_INF, F("  Generate Action: tempC >= GA_TEMP_MAX"));
      return true;
    }
  }
  // if no action was not generated, return false
  return false;
}


