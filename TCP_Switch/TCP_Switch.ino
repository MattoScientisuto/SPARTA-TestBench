int relayPin = 8;
unsigned long commandTime = 0; // variable to store the time when the command is received
int delayDuration = 0; // variable to store the delay duration

void setup() {
  Serial.begin(9600);
  pinMode(relayPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil(',');
    String param = Serial.readStringUntil('\n');
    
    // Starts a timer when a command is received
    commandTime = millis();

    if (command == "H") {
      digitalWrite(relayPin, HIGH);
      Serial.println("HEATING");
      delayDuration = param.toInt(); // Store the delay duration
    } 
    else if (command == "C") {
      digitalWrite(relayPin, LOW);
      Serial.println("STOPPED");
    }
  }

  // Check if a delay command is ongoing
  if (millis() - commandTime < delayDuration) {
    // If the time hasn't elapsed, continue doing other things
    // You can add other code here to execute concurrently
  } 
  else {
    // If the time has elapsed, do something (e.g., turn off the relay)
    digitalWrite(relayPin, LOW);
  }
}
