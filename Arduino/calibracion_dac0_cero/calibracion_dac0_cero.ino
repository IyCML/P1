


#include <efc.h>
#include <Wire.h>
#include "SPI.h"
#include "math.h"



void setup() {
  Serial.begin(9600);
  // put your setup code here, to run once:

  analogReadResolution(12);
  analogWriteResolution(12);
  pinMode (DAC0,OUTPUT);

  analogWrite(DAC0, 4095);  
   
}

void loop() {
	

}



