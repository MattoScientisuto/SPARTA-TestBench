int relayPin1 = 2;
int relayPin2 = 3;
unsigned long commandTime = 0; // variable to store the time when the command is received
int delayDuration = 0; // variable to store the delay duration

void setup() {
  Serial.begin(4800);
  pinMode(relayPin1, OUTPUT);
  pinMode(relayPin2, OUTPUT);
  digitalWrite(relayPin1, HIGH);
  digitalWrite(relayPin2, HIGH);
}

void loop() {
  if (Serial.available() > 0) {
    // String command = Serial.readStringUntil(',');
    // String param = Serial.readStringUntil('\n');

    char command = Serial.read();
    // Starts a timer when a command is received
    // commandTime = millis();

    // PUSH
    if (command == 'W') {
      digitalWrite(relayPin1, LOW);
      digitalWrite(relayPin2, HIGH);
      // delayDuration = param.toInt(); // Store the delay duration
    } 

    // PULL
    if (command == 'C') {
      digitalWrite(relayPin1, HIGH);
      digitalWrite(relayPin2, LOW);
    }

    // STOP
    if (command == 's') {
      digitalWrite(relayPin1, HIGH);
      digitalWrite(relayPin2, HIGH);
    }
  }
  delay(10);
}

//
//int relayPin1 = 2;
//int relayPin2 = 3;
//unsigned long commandTime = 0; // Time when the command is received
//unsigned long moveDuration = 0; // Duration for the movement
//bool isMoving = false; // Flag to check if the actuator is moving
//
//void setup() {
//  Serial.begin(9600);
//  pinMode(relayPin1, OUTPUT);
//  pinMode(relayPin2, OUTPUT);
//  digitalWrite(relayPin1, HIGH);
//  digitalWrite(relayPin2, HIGH);
//}
//
//void loop() {
//  if (Serial.available() > 0) {
//    char command = Serial.read();
//    
//    if (command == 'W') {
//      String durationStr = Serial.readStringUntil('\n');
//      moveDuration = durationStr.toInt();
//      
//      digitalWrite(relayPin1, LOW);
//      digitalWrite(relayPin2, HIGH);
//      commandTime = millis(); // Start timer
//      isMoving = true;
//    } 
//    else if (command == 'C') {
//      digitalWrite(relayPin1, HIGH);
//      digitalWrite(relayPin2, LOW);
//      isMoving = false; // Move fully, no timer
//    }
//    else if (command == 's') {
//      digitalWrite(relayPin1, HIGH);
//      digitalWrite(relayPin2, HIGH);
//      isMoving = false; // Stop immediately
//    }
//  }
//
//  // Stop the movement after the specified duration for 'W' command
//  if (isMoving && (millis() - commandTime >= moveDuration)) {
//    digitalWrite(relayPin1, HIGH);
//    digitalWrite(relayPin2, HIGH);
//    isMoving = false; // Stop the actuator
//  }
//}
