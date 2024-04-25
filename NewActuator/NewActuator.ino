int relayPin1 = 2;
int relayPin2 = 3;
unsigned long commandTime = 0; // variable to store the time when the command is received
int delayDuration = 0; // variable to store the delay duration

void setup() {
  Serial.begin(9600);
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

  //   // Check if a delay command is ongoing
  // if (millis() - commandTime < delayDuration) {
  //   // If the time hasn't elapsed, continue doing other things
  //   // You can add other code here to execute concurrently
  // } 
  // else {
  //   // If the time has elapsed, do something (e.g., turn off the relay)
  //   digitalWrite(relayPin1, HIGH);
  //   digitalWrite(relayPin2, HIGH);
  // }
}
