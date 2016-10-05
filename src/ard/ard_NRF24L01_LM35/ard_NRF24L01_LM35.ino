// http://invent.module143.com/daskal_tutorial/rpi-3-tutorial-14-wireless-pi-to-arduino-communication-with-nrf24l01/

// includes
#include<SPI.h>
#include<RF24.h>
 
// ce, csn pins
RF24 radio(9, 10);

// setup
void setup(void){
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  radio.openWritingPipe(0xF0F0F0F0E1LL);
  radio.enableDynamicPayloads();
  radio.powerUp();
}

// iter parameters
int iIter=0;
char cIter[4];
String sIter="";
char text[128] = "\nI love you Natalia ";

// loop
void loop(void){
  
  // create text message
  char msg[128];
  strncpy(text,msg,sizeof(msg));
  sIter = String(iIter++);
  sIter.toCharArray(cIter,sizeof(cIter));
  strcat(text,cIter);
  
  // send message
  radio.write(&text, sizeof(text));

  // delay
  delay(1000);
}

