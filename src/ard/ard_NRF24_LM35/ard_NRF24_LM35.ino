// http://invent.module143.com/daskal_tutorial/rpi-3-tutorial-14-wireless-pi-to-arduino-communication-with-nrf24l01/




// --------------------------------------------------------------
// INCLUDES
#include <SPI.h>
#include <RF24.h>
#include "config.h"
#include "action.h"
#include "log.h"
#include "rxtx.h"




// radio main
RF24 radioMain(PIN_CE, PIN_CSN);

// iter parameters
const bool SERIAL_ON = true;
int loop_iter=0;




// --------------------------------------------------------------
// SETUP
void setup(void){
  
  // serial
  if (LOG_LVL < LOG_OFF) {
    Serial.begin(115200); // 9600, 57600, 115200
  }
  
  // LM35 setup (see LM35 ref: http://playground.arduino.cc/Main/LM35HigherResolution)
  analogReference(INTERNAL);

  // NRF24L01 setup
  radioMain.begin();
  // message and ACK
  radioMain.setPayloadSize(PAYLOAD_MAX_SIZE);
  radioMain.enableDynamicPayloads();    // instead of: radioMain.setPayloadSize(int);
  radioMain.setAutoAck(true);
  radioMain.enableAckPayload();
  radioMain.setRetries(1,15);           // min ms between retries, max number of retries
  // channel and pipes
  radioMain.setChannel(0x76);
  radioMain.openReadingPipe(1, pipes[PIPE_R]);
  radioMain.openWritingPipe(pipes[PIPE_W]);
  // rate, power
  radioMain.setDataRate(RF24_1MBPS);  // with RF24_250KBPS <10% success...
  radioMain.setPALevel(RF24_PA_HIGH);
  //radioMain.powerUp();
  // role
  //role = ROLE_RX;
  // print details (printf_begin();)
  //radioMain.printDetails();
}




// --------------------------------------------------------------
// LOOP
void loop(void){

  // RX loop
  RXTX::rx(radioMain, true);

}



