


#include <efc.h>
#include <Wire.h>
#include "SPI.h"
#include "math.h"



#define SERIAL_BUFFER_SIZE 128

// Para lectura de canales
int iter = 2000;
int skip_num = 20;
int n_chan = 12; 
int i = 0;
int j = 0;
int k = 0;

bool read_ind = 0;
int ana = 0;
long ana_sum = 0;
float ana_avg[12];
float ana_avg_ant[12];
int pin_tec_onoff = 49;

int digi_tec = 0;
int digi_tec_ant = 0;
int tec_onoff = 1;
int tec_onoff_ant = 1;

float temp_setpoint = 16.55;
float temp_setpoint1 = 0.;
float temp_actual = 0.0;
float corriente_termistor = 0.0001;
float tension_tec = 0.;

float rango_dac0 = 2.159;
float offset_dac0 = 0.541;

float a_ter = 0.0011279;
float b_ter = 0.00023429;
float c_ter = 0.000000087298;
float r_termistor = 10000.;

char serial_com[400];


void setup() {
  Serial.begin(9600);
  // put your setup code here, to run once:

  analogReadResolution(12);
  analogWriteResolution(12);
  pinMode (DAC0,OUTPUT);
  pinMode(pin_tec_onoff, OUTPUT); 
    
	// TEC:
    if (tec_onoff == 0){
		digitalWrite(pin_tec_onoff, LOW); 	
	}else{
		digitalWrite(pin_tec_onoff, HIGH); 	
	}  	
	// Temperatura TEC:
	r_termistor = r_to_volt(temp_setpoint, a_ter, b_ter, c_ter);	
	tension_tec = r_termistor*corriente_termistor;
	digi_tec = (tension_tec-offset_dac0)*float(pow(2,12))/rango_dac0;
	analogWrite(DAC0, digi_tec);	

  tec_onoff_ant = tec_onoff;
  digi_tec_ant = digi_tec;

  // Lectura de canales
	for (k =0;k<n_chan;k++){
	  ana_avg[k] = 0.0;
	  }  
	  
	for (k =0;k<n_chan;k++){
	  ana_avg_ant[k] = 0.0;
	  } 	  
  
}

void loop() {

    while(Serial.available() > 500) {
      char t = Serial.read();
    }
  

		if(Serial.available() >= 2){  
			// fill array
			//flag_hay_datos = 1;
			
			Serial.readBytes((char*)&read_ind, sizeof(read_ind));
			Serial.readBytes((char*)&tec_onoff, sizeof(tec_onoff));
			Serial.readBytes((char*)&temp_setpoint, sizeof(temp_setpoint));     

			r_termistor = r_to_volt(temp_setpoint, a_ter, b_ter, c_ter);	
			tension_tec = r_termistor*corriente_termistor;
			digi_tec = (tension_tec-offset_dac0)*float(pow(2,12))/rango_dac0;

		}
	
      // TEC on-off:
      if (tec_onoff_ant != tec_onoff){
        if (tec_onoff == 0){
          digitalWrite(pin_tec_onoff, LOW);   
        }else{
          digitalWrite(pin_tec_onoff, HIGH);  
        }   
      }
     
      // Temperatura TEC :
      if (digi_tec_ant != digi_tec){
        analogWrite(DAC0, digi_tec);  
      }

      tec_onoff_ant = tec_onoff;
      digi_tec_ant = digi_tec;




		  // Medicion de los canales analogicos
 		  i = i + 1;
		  ana = analogRead(j); 
		  
		  if (i > skip_num){
			ana_sum = ana_sum + ana;   
		  }
		  
		  
		  if (i == iter){

			
			ana_avg[j] = ana_sum/(iter-skip_num)*3.3/4095.;
			ana_sum = 0;

				   
			i = 0;
			j = j + 1;

			if (j == n_chan){
				

				temp_actual = r_to_temp(ana_avg[0]/corriente_termistor,a_ter,b_ter,c_ter);
				temp_setpoint1 = r_to_temp(ana_avg[2]/corriente_termistor,a_ter,b_ter,c_ter);

				
			  delay(200);	
			  sprintf(serial_com, "%d, %f ,%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f    \n",true, temp_actual, ana_avg[1], temp_setpoint1, ana_avg[3], ana_avg[4], ana_avg[5], ana_avg[6], ana_avg[7], ana_avg[8], ana_avg[9], tec_onoff, temp_setpoint);
			  Serial.write(serial_com);
			  Serial.flush();
			  delay(500);
			  
			  j = 0;
			  for (k = 0;k<n_chan;k++){
				 ana_avg[k] = 0.0;
			  }
    
			  
			}
		  }



}


float r_to_volt(float temp,float a, float b, float c){
	
	temp = (double)temp + 273.1;
	a = (double)a;
	b = (double)b;
	c = (double)c;
	
	double x = 1./c*(a - 1./temp);  
	double y = sqrt(pow(b/3/c,3) + pow(x/2,2));
	double r = exp(pow(y-x/2.,1./3.) - pow(y+x/2.,1./3.));
	r = (float) r;
	
	return r;
}


float r_to_temp(float r,float a, float b, float c){

	r = (double)r;
	a = (double)a;
	b = (double)b;
	c = (double)c;	
	
	double temp = a + b*log(r) + c*pow(log(r) ,3);
	temp = 1./temp;
	
	temp = temp - 273.1;
	temp = (float)temp;
		
	return temp;
}
