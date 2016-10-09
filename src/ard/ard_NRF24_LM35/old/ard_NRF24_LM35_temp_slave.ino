// http://invent.module143.com/daskal_tutorial/rpi-3-tutorial-14-wireless-pi-to-arduino-communication-with-nrf24l01/




// --------------------------------------------------------------
// INCLUDES
#include <SPI.h>
#include <RF24.h>




// --------------------------------------------------------------
// PARAMETERS

// 123456789_123456789_123456789_-2-456789_123456789_ - STRING_LENGTH_RULER

// NRF24L01 communication
const short int PIPE_R = 0;
const short int PIPE_W = 1;
const uint64_t pipes[2] = {0xE8E8F0F0E1LL, 0xF0F0F0F0E1LL};
short int role;
const short int ROLE_TX = 0;
const short int ROLE_RX = 1;
const short int PAYLOAD_MAX_SIZE = 32;      // defined by NRF24 datasheet
const short int PAYLOAD_ACK_MAX_SIZE = 32;  // defined by NRF24 datasheet

// NRF24L01 pins: CE, CSN
const short int PIN_CE = 9;
const short int PIN_CSN = 10;
RF24 radio(PIN_CE, PIN_CSN);

// Message RX
const short int charMsgRxSize = PAYLOAD_MAX_SIZE;
char charMsgRx[charMsgRxSize];
String strMsgRx;
// Message TX
const short int charMsgTxSize = PAYLOAD_MAX_SIZE;
char charMsgTx[charMsgTxSize];
String strMsgTx;
// ACK RX
const short int charAckRxSize = PAYLOAD_ACK_MAX_SIZE;
char charAckRx[charAckRxSize];
String strAckRx;
// ACK TX
const short int charAckTxSize = PAYLOAD_ACK_MAX_SIZE;
char charAckTx[charAckTxSize];
String strAckTx;

// LM35 pins and tempC
const short int PIN_ANALOG_IN_LM35 = 5;
float tempC;

// iter parameters
const bool SERIAL_ON = true;
int loop_iter=0;




// --------------------------------------------------------------
// FUNCTIONS

// -------------------
// TX temperature to Raspberry Pi
// return: true(ACK_RX), false(NO_ACK_RX)
bool tx_temp() {

  // wait a bit for the Rasberry Pi to get ready for RX mode
  delay(20);
  
  // TX stop listening RX
  radio.stopListening();
    
  // get temperature in celsius [tempF = (tempC * 1.8) + 32]
  tempC = analogRead(PIN_ANALOG_IN_LM35) / 9.31;
  
  // create message
  strMsgTx = "Tem=" + String(tempC) + ", iter=" + String(loop_iter++);
  strMsgTx.toCharArray(charMsgTx, min(strMsgTx.length()+1,charMsgTxSize));
  
  // TX message
  if(SERIAL_ON) {Serial.print("TX: \""); Serial.print(strMsgTx);Serial.println("\"");}
  // No ACK received:
  if (!radio.write(&charMsgTx, sizeof(charMsgTx))){
    if(SERIAL_ON) {Serial.println("  ACK_RX: NO");}
    return false;
  // ACK_RX:
  // issue!!!: when a row of msg is read, after TX stops, RX keeps reading ACKs for 2-3 times
  } else {
    // ACK_RX (ACK payload OK):
    // issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
    if (radio.isAckPayloadAvailable()) {
      radio.read(&charAckRx, sizeof(charAckRx));
      strAckRx = String(charAckRx);
      if(SERIAL_ON) {Serial.print("  ACK_RX: YES\n  ACK_RX_payload: \"");Serial.print(strAckRx);Serial.println("\"");}
    // ACK_RX (ACK payload <empty>): 
    } else {
      if(SERIAL_ON) {Serial.println("  ACK_RX: YES\n  ACK_RX_payload: <empty>");}
    }
    return true;
  }
}




// --------------------------------------------------------------
// SETUP
void setup(void){
  
  // serial
  if (SERIAL_ON) {Serial.begin(115200);}
  
  // LM35 setup (see LM35 ref: http://playground.arduino.cc/Main/LM35HigherResolution)
  analogReference(INTERNAL);

  // NRF24L01 setup
  radio.begin();
  // message and ACK
  radio.setPayloadSize(PAYLOAD_MAX_SIZE);
  radio.enableDynamicPayloads();    // instead of: radio.setPayloadSize(int);
  radio.setAutoAck(true);
  radio.enableAckPayload();
  radio.setRetries(1,15);           // min ms between retries, max number of retries
  // channel and pipes
  radio.setChannel(0x76);
  radio.openReadingPipe(1, pipes[PIPE_R]);
  radio.openWritingPipe(pipes[PIPE_W]);
  // rate, power
  radio.setDataRate(RF24_1MBPS);  // with RF24_250KBPS <10% success...
  radio.setPALevel(RF24_PA_MIN);
  //radio.powerUp();
  // role
  //role = ROLE_RX;
  // print details (printf_begin();)
  //radio.printDetails();
}




// --------------------------------------------------------------
// LOOP
void loop(void){
  
  // RX start listening TX
  radio.startListening();
  
  // RX loop: wait for a message
  if(SERIAL_ON) {Serial.println("\nRX: waiting message...");}
  while(!radio.available()) {
    delay(10);
  }

  // ACK_TX payload before RX
  // issue!!!: ACK payload is getting delayed by 1 (ACK_RX[i]=ACK_TX[i-1]), but this does not affect to a normal ACK
  strAckTx = "ACK from Arduino";
  strAckTx.toCharArray(charAckTx, min(strAckTx.length()+1,charAckTxSize));
  radio.writeAckPayload(1, charAckTx, sizeof(charAckTx));
  
  // RX message
  radio.read(&charMsgRx, sizeof(charMsgRx));
  strMsgRx = String(charMsgRx);
  if(SERIAL_ON) {Serial.print("RX: \"");Serial.print(strMsgRx);Serial.println("\"");}
  if(SERIAL_ON) {Serial.print("  ACK_TX_payload: \"");Serial.print(strAckTx);Serial.println("\"");}

  // handle RX message
  if (strcmp(strMsgRx.c_str(),String("GET,TEMP").c_str()) == 0) {
    if(SERIAL_ON) {Serial.print("  Handled message \"");Serial.print(strMsgRx);Serial.println("\"");}
    // TX response
    tx_temp();
  } else {
    if(SERIAL_ON) {Serial.print("  Unhandled message \"");Serial.print(strMsgRx);Serial.println("\"");}
  }
}



