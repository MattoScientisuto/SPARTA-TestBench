int relayPin = 8;

void setup() {
  Serial.begin(9600);
  Serial.println("Connected");
  pinMode(relayPin, OUTPUT);
}

void loop() {
  if(Serial.available() > 0){
    String command = Serial.readStringUntil(',');
    String param = Serial.readStringUntil('\n');
    
    if(command == "H"){
      digitalWrite(relayPin, HIGH);
      delay(param.toInt());
      digitalWrite(relayPin, LOW);
    }
    else if(command == "C"){
      digitalWrite(relayPin, LOW);
    }
  }
}
