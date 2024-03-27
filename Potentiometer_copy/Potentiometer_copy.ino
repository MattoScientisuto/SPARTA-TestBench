float pos;                      // Actuator Position
float conNum = 0.0069;         // Constant to convert ADC to Inches
                                // Equal to (951 (ADC at 4") - 44 (ADC at 0")/4")^-1
const int relay1 = 2;
const int relay2 = 3;
const int pushButton1 = 8;
const int pushButton2 = 9;

void actuatorRetract();
void actuatorExtend();
void actuatorStop();

void setup() {
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  pinMode(pushButton1, INPUT_PULLUP);
  pinMode(pushButton2, INPUT_PULLUP);
  pinMode(A1, INPUT);

  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);

  Serial.begin(9600);
}

void loop() {
  // Check if data is available to read from serial
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read the incoming byte

    // Act based on the received command
    switch (command) {
      case 'W':
        actuatorExtend();
        break;
      case 's':  // Lowercase 's' for stop command
        actuatorStop();
        break;
      case 'C':
        actuatorRetract();
        break;
      default:
        // Handle unknown command
        break;
    }

    // Clear the serial buffer
    while (Serial.available() > 0) {
      Serial.read(); // Read and discard any remaining bytes
    }
  }

  // Read potentiometer and print current position
  pos = readPotentiometer();
  Serial.print("Current Position: ");
  Serial.println(pos);
}

void actuatorExtend(){
  digitalWrite(relay1, LOW);
  digitalWrite(relay2, HIGH);
}

void actuatorRetract(){
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, LOW);
}

void actuatorStop(){
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
}

/*Function to Read Potentiometer and Convert it to Inches*/
float readPotentiometer(void){
  float pos;
  pos = conNum*(analogRead(A1) - 1); // 44 ADC is equal to 0"
  return pos;
}
