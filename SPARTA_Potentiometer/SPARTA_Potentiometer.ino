/* Firgelli Automations
 * Limited or no support: we do not have the resources for Arduino code support
 * 
 * Program enables momentary direction control of actuator using push button
 */
 
#include <elapsedMillis.h>
elapsedMillis timeElapsed;

int RPWM = 10;   
int LPWM = 11;
int sensorPin = A0;

int sensorVal;
int Speed=255;
float strokeLength = 6.0;                           //customize to your specific stroke length
float extensionLength;

int maxAnalogReading;
int minAnalogReading;

void setup() {
  pinMode(RPWM, OUTPUT);
  pinMode(LPWM, OUTPUT);
  pinMode(sensorPin, INPUT);
  Serial.begin(9600);
  maxAnalogReading = moveToLimit(1);
  minAnalogReading = moveToLimit(-1);
}

void loop(){
  Serial.println("Extending...");
  sensorVal = analogRead(sensorPin);
  while(sensorVal < maxAnalogReading){
    driveActuator(1, Speed);
    displayOutput();  
    delay(20);
  }
  driveActuator(0, Speed);
  delay(1000);
  
  Serial.println("Retracting...");
  sensorVal = analogRead(sensorPin);
  while(sensorVal > minAnalogReading){
    driveActuator(-1, Speed);
    displayOutput();  
    delay(20);
  }
  driveActuator(0, Speed);
  delay(1000);
}

int moveToLimit(int Direction){
  int prevReading=0;
  int currReading=0;
  do{
    prevReading = currReading;
    driveActuator(Direction, Speed);
    timeElapsed = 0;
    while(timeElapsed < 200){ delay(1);}           //keep moving until analog reading remains the same for 200ms
    currReading = analogRead(sensorPin);
  }while(prevReading != currReading);
  return currReading;
}

float mapfloat(float x, float inputMin, float inputMax, float outputMin, float outputMax){
 return (x-inputMin)*(outputMax - outputMin)/(inputMax - inputMin)+outputMin;
}

void displayOutput(){
  sensorVal = analogRead(sensorPin);
    extensionLength = mapfloat(sensorVal, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
    Serial.print("Analog Reading: ");
    Serial.print(sensorVal);
    Serial.print("\tActuator extension length: ");
    Serial.print(extensionLength);
    Serial.println(" inches");  
}

void driveActuator(int Direction, int Speed){
  switch(Direction){
    case 1:       //extension
      analogWrite(RPWM, Speed);
      analogWrite(LPWM, 0);
      break;
   
    case 0:       //stopping
      analogWrite(RPWM, 0);
      analogWrite(LPWM, 0);
      break;

    case -1:      //retraction
      analogWrite(RPWM, 0);
      analogWrite(LPWM, Speed);
      break;
  }
}