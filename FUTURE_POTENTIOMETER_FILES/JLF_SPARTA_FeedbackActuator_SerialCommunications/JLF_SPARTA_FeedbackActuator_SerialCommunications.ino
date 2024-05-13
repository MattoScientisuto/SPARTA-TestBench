#include <elapsedMillis.h>
elapsedMillis timeElapsed;

int RPWM = 10;   
int LPWM = 11;
int sensorPin = A0; 

int sensorVal;
int Speed=255;
float strokeLength = 14.605; //cm                          //customize to your specific stroke length
float extensionLength;

int maxAnalogReading;
int minAnalogReading;

int startSensorVal;
float extensionDist = 0.;


int needToExtend = 1;
int startedExtending = 0;
int readyForNewValue = 1;
float startPosition;
int doneExtending;

float desiredPosition = 0.;

int currentPositionInt;
float currentPosition;



/////////////////  START DRIVEACTUATOR() //////////////////////
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
/////////////////  END DRIVEACTUATOR() //////////////////////



/////////////////  START MAPFLOAT() //////////////////////
float mapfloat(float x, float inputMin, float inputMax, float outputMin, float outputMax){
 return (x-inputMin)*(outputMax - outputMin)/(inputMax - inputMin)+outputMin;
}
/////////////////  END MAPFLOAT() //////////////////////



/////////////////  START SETUP() //////////////////////
void setup() {
  pinMode(RPWM, OUTPUT);
  pinMode(LPWM, OUTPUT);
  pinMode(sensorPin, INPUT);
  Serial.begin(9600);
  maxAnalogReading = 863; //from lab testing
  minAnalogReading = 0;


  currentPositionInt = analogRead(sensorPin);
  currentPosition = mapfloat(currentPositionInt, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
  Serial.println(currentPosition);
  
//  sensorVal = analogRead(sensorPin);
//  if (sensorVal != 0){
//    while (sensorVal > 0){
//      sensorVal = analogRead(sensorPin);
//      driveActuator(-1, Speed);
//      //Serial.println("Retracting");
//    } 
//  }

}

/////////////////  END SETUP() //////////////////////




/////////////////  START LOOP() //////////////////////
void loop(){
//extensionDist = 1.;

//  Serial.println("Serial.available() = " + String(Serial.available()));
//  Serial.println("readyForNewValue = " + String(readyForNewValue));
//  Serial.println("startedExtending = " + String(startedExtending));
//  Serial.println("doneExtending = " + String(doneExtending));
//  Serial.println("currentPosition = " + String(currentPosition));
//  Serial.println("desiredPosition = " + String(desiredPosition));
//  Serial.println("");
//  delay(2000);


  currentPositionInt = analogRead(sensorPin);
  currentPosition = mapfloat(currentPositionInt, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
  Serial.println(currentPosition);
  delay(0.1);

  //read in value to extend
  if ((Serial.available() > 0) && (readyForNewValue == 1) && (startedExtending == 0)) {
    Serial.println("If 1");
    currentPositionInt = analogRead(sensorPin);
    currentPosition = mapfloat(currentPositionInt, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
    Serial.println(currentPosition);
    if (Serial.peek() == '\n') {
      // Clear the newline character from the buffer
      Serial.read();
      //Serial.println("Cleared newline");
    
    } 
      
    else {
      extensionDist = Serial.parseFloat();
      //Serial.println("Distance to extend: " + String(extensionDist));
      // Optional: If you want to ensure only one value is read, you can clear the remaining bytes from the buffer
      while (Serial.available() > 0) {
        //Serial.println("reading");
        Serial.read();
        readyForNewValue = 0;
        currentPositionInt = analogRead(sensorPin);
        currentPosition = mapfloat(currentPositionInt, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
        Serial.println(currentPosition);
      }
    }
    
    if (extensionDist == -1.){
       while (true){
        //read position
        currentPositionInt = analogRead(sensorPin);
        currentPosition = mapfloat(currentPositionInt, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
        Serial.println(currentPosition);
        if (currentPosition > 0.){
          //read position
          currentPositionInt = analogRead(sensorPin);
          currentPosition = mapfloat(currentPositionInt, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
          Serial.println(currentPosition);
          
          //drive actuator
          driveActuator(-1, Speed);        
        }

        if (currentPosition <= 0.){
          //read position
          currentPositionInt = analogRead(sensorPin);
          currentPosition = mapfloat(currentPositionInt, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
          Serial.println(currentPosition);

          //stop actuator
          driveActuator(0, Speed);

          //reset status
          doneExtending = 0;
          startedExtending = 0;
          readyForNewValue = 1;
          desiredPosition = 0.;
          break;
        }
      }
    }
  }
  

  if ((readyForNewValue == 0) && (startedExtending == 0) && (doneExtending == 0)){
    Serial.println("If 2");
    //read current position

    //calculate desired position
    desiredPosition += extensionDist;
    
    startedExtending = 1;
  }

  if ((readyForNewValue == 0) && (startedExtending == 1) && (doneExtending == 0)){
    if (currentPosition >= desiredPosition){
      //Serial.println("If 3");
    
      while (true){
        //Serial.println("If 3 While Loop");
        if (currentPosition < desiredPosition){
          Serial.println("If 3 While Loop If 1");
          //read position
          currentPositionInt = analogRead(sensorPin);
          currentPosition = mapfloat(currentPositionInt, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
          Serial.println(currentPosition);

          //drive actuator
          driveActuator(1, Speed);        
        }
      

        if (currentPosition >= desiredPosition){
          Serial.println("If 3 While Loop If 2");
          currentPositionInt = analogRead(sensorPin);
          currentPosition = mapfloat(currentPositionInt, float(minAnalogReading), float(maxAnalogReading), 0.0, strokeLength);
          Serial.println(currentPosition);
          
          //stop actuator
          driveActuator(0, Speed);          
          
          //reset status
          doneExtending = 0;
          startedExtending = 0;
          readyForNewValue = 1;
          break;
        }
      }
    }
  } 
}

/////////////////  END LOOP() //////////////////////
