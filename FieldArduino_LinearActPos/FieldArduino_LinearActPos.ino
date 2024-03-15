//Actuator Specifications
int maxStroke;
int minStroke;

// Input Variables (Pins)
const int Xpin=10;
const int Rpin=11;
const int sensorPin=3;
// Hall Effect Sensor Input
const int sensorPin2=4;
int sensorCount2;


// Motor Function Variables
int targetNumber;
int currentPosition;
int lastPosition=0;
bool active = false;
bool EOSFlag=false;

// Sensor Readings
int sensorValue;
int lastSensorValue = LOW;
int sensorValue2;
int lastSensorValue2 = LOW;

// Variables for Debounce
const unsigned long motionTimeout = 2000;  // Adjust this value based on your requirements (in milliseconds)
const unsigned long CALIBRATION_TIMEOUT=3000; // Adjust this value based on your requirements (in milliseconds)
unsigned long lastMotionTime = millis();

// Position Variables
unsigned long pulseCount = 0;
int direction = 0;  // 0: Stopped, 1: Moving Forward, -1: Moving Backward




void setup() {
  pinMode(Xpin, OUTPUT);
  pinMode(Rpin, OUTPUT);
  pinMode(sensorPin, INPUT_PULLUP);
  pinMode(sensorPin2, INPUT_PULLUP);
  Serial.begin(115200);

  homingRoutine();
  calibrateActuator();
}

void homingRoutine() {
  active=true;
  Serial.println("Homing Initiated");
  digitalWrite(Xpin, LOW);
  digitalWrite(Rpin, HIGH);
  while (!EOSFlag) {
    direction=-1;
    readSensor();
    isEndOfStroke();
    // Move actuator to full retraction
    
  }
  direction=0;
  minStroke=currentPosition;
  Serial.println("Homing Completed");
}

void calibrateActuator() {
  Serial.println("Calibration Initiated");
  active = true;
  // Reset variables
  pulseCount = 0;
  currentPosition = 0;
  lastMotionTime=millis();

  // Move actuator to full extension
  digitalWrite(Xpin, HIGH);
  digitalWrite(Rpin, LOW);
  direction=1;

  // Wait until the end of stroke is reached during calibration
  while (!isEndOfStroke()) {
    readSensor();

    // Add a timeout condition to avoid infinite loop
    if (millis() - lastMotionTime > motionTimeout) {
      Serial.println("Calibration Timeout");
      stopMotor();
      maxStroke=currentPosition;
      direction=0;
      // Print the calibration results
        Serial.print("Calibration Complete. Minimum Stroke: ");
        Serial.print(minStroke);
        Serial.print(" Maximum Stroke: ");
        Serial.println(maxStroke);
        targetNumber=((maxStroke+minStroke)/2);
        break;
    }
  }
}

void loop() {
if (!active && Serial.available() > 0) {
  String serialInput = Serial.readStringUntil('\n');
  Serial.print("Received: ");
  Serial.println(serialInput);
  if (serialInput.length() > 0) {
    targetNumber = serialInput.toInt();
    Serial.print("Target number: ");
    Serial.println(targetNumber);
    EOSFlag = false;
  }
  // Clear the serial buffer
  while (Serial.available()) {
    Serial.read();
  }
}

  if (targetNumber != currentPosition) {
    active = true;
    movement();
  } 
  /*
  if (!active) {
   Serial.println("Waiting for Input"); 
   return;
  } */
  if (active && targetNumber == currentPosition) {
   stopMotor();
   Serial.println("Target Met");
  }
}

void movement() {
  if (targetNumber > currentPosition) {
    digitalWrite(Xpin,HIGH);
    digitalWrite(Rpin,LOW);
    //Serial.println(" Extending");
    direction = 1;
  } else if (targetNumber < currentPosition) {
    digitalWrite(Rpin,HIGH);
    digitalWrite(Xpin,LOW);
    direction = -1;
    //Serial.println("Retracting");
  } else if (targetNumber == currentPosition) {
    stopMotor();
    delay(10);
  }
  if(active) {
    readSensor();
  }
  if (isEndOfStroke()) {
    return;  // Skip further movement actions
  }
}

void readSensor() {
  sensorValue = digitalRead(sensorPin);
  if(lastSensorValue != sensorValue) {
    lastSensorValue = sensorValue;
    pulseCount = pulseCount + direction;
    Serial.print("Sensor 1: ");
    Serial.println(pulseCount);
  }
  sensorValue2 = digitalRead(sensorPin2);
  if(lastSensorValue2 != sensorValue2) {
    lastSensorValue2 = sensorValue2;
    sensorCount2=sensorCount2+direction;
    pulseCount = pulseCount + direction;
    Serial.print("Sensor 2: ");
    Serial.println(sensorCount2);
    Serial.print("Current Position: ");
    Serial.println(currentPosition);
  }
  currentPosition = pulseCount;
}


void stopMotor() {
 if (active) {
   active=false;
   digitalWrite(Xpin,LOW);
   digitalWrite(Rpin,LOW);
  }
}

bool isEndOfStroke() {
  // Check if there is motion (changes in the pulse count)
  if (active && (currentPosition != lastPosition)) {
    lastMotionTime = millis();  // Update the time of the last motion
    lastPosition = currentPosition;
    EOSFlag=false;
  }

  // Check if there is no motion for the specified timeout
  if (active && ((millis() - lastMotionTime) > motionTimeout)) {
    if(EOSFlag!=true) {
      Serial.print("Timeout - ");
      Serial.println("At limit");
      EOSFlag=true;
    }
    direction=0;
    stopMotor();
    return true;
  }
  return false;
}