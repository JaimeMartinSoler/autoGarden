 /*
    // ----------------------------------------------------------------------
    // --- ard_GPIO_LM35.ino                                              ---
    // ----------------------------------------------------------------------
    // --- autoGarden main Arduino file, to manage sensors and RPi comm.  ---
    // --- RPi requirements: execute twitter_GPIO.py                      ---
    // --- RPi comm.: GPIO (output 100ms pulse through pin 13)            ---
    // --- Sensor: LM35d analog temperature sensor (analog pin 5)         ---
    // --- LM35 ref: http://playground.arduino.cc/Main/LM35HigherResolution -
    // ----------------------------------------------------------------------
    // --- Author: Jaime Martin Soler                                     ---
    // --- Date  : 27/09/2016                                             ---
    // ----------------------------------------------------------------------
*/


// ----------------------------------------------------------------------
// INCLUDES




// ----------------------------------------------------------------------
// PARAMETERS

// PINS
const int PIN_BROKEN_VCC = 8;   // BROKEN, ALWAYS VCC
const int PIN_OUT_RPI = 13;
const int ANALOG_PIN_IN_LM35 = 5;     

// OTHER PARAMETERS
const int DELAY_LOOP = 2000;
const bool SERIAL_ON = true;
int iter_loop = 0;
bool first_pulse = true;

// tempC is the measured temperature, by LM35
float tempC = 0.0;

// (tempC >= TEMPC_RPI) -> HIGH to PIN_OUT_RPI, for TIME_RPI_PULSE ms
const float TEMPC_RPI = 30.0;
const int TIME_RPI_PULSE = 100;

// If PIN_OUT_RPI got a pulse, no more pulses will be make for TIME_RPI_IGNORED ms
// millis() returns unsigned long, we have to use this type or it will fail
const unsigned long TIME_RPI_IGNORED = 30000;
unsigned long time_last_RPI_pulse = 0;




// ----------------------------------------------------------------------
// SETUP

void setup() {
  
  // Raspberry Pi
  pinMode(PIN_OUT_RPI, OUTPUT);
  digitalWrite(PIN_OUT_RPI, LOW);
  
  // LM35 (see LM35 ref: http://playground.arduino.cc/Main/LM35HigherResolution)
  analogReference(INTERNAL);

  // time_last_RPI_pulse setup first time
  first_pulse = true;
  time_last_RPI_pulse = 0;
  
  // Serial begin
  if (SERIAL_ON) {Serial.begin(9600);}
}




// ----------------------------------------------------------------------
// MAIN LOOP

void loop() {

  // get temperature in celsius [tempF = (tempC * 1.8) + 32]
  tempC = analogRead(ANALOG_PIN_IN_LM35) / 9.31;
  if (SERIAL_ON) {Serial.print(iter_loop++); Serial.print(" : Temp="); Serial.print(tempC); Serial.print("C, ");}

  // only if the last pulse was more than TIME_RPI_IGNORED ago, check for more pulses
  if (((millis() - time_last_RPI_pulse) >= TIME_RPI_IGNORED) || first_pulse) {
    if (SERIAL_ON) {Serial.print("Checking=YES, ");}
    
    // if (tempC >= TEMPC_RPI) send a pulse to PIN_OUT_RPI and update time_last_RPI_pulse
    if (tempC >= TEMPC_RPI) {
      digitalWrite(PIN_OUT_RPI, HIGH);
      delay(TIME_RPI_PULSE);
      digitalWrite(PIN_OUT_RPI, LOW);
      time_last_RPI_pulse = millis();
      first_pulse = false;
      if (SERIAL_ON) {Serial.print("Pulse=YES, tLast="); Serial.println(time_last_RPI_pulse);}
    } else {
      if (SERIAL_ON) {Serial.print("Pulse=NO , tLast="); Serial.println(time_last_RPI_pulse);}
    }
  } else {
    if (SERIAL_ON) {Serial.print("Checking=NO , Pulse=NO , tLast="); Serial.println(time_last_RPI_pulse);}
  }
  
  // delay
  delay(DELAY_LOOP);
}


