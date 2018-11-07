#define CURRENT1_PIN A0
#define CURRENT2_PIN A1
#define SERVO1_PIN 11
#define SERVO2_PIN 10

#include <Servo.h>


Servo servo1, servo2;
char msg_type;


void setup() {
  servo1.attach(SERVO1_PIN, 900, 2100);
  servo2.attach(SERVO2_PIN, 900, 2100);
  
  pinMode(CURRENT1_PIN, INPUT);
  pinMode(CURRENT2_PIN, INPUT);
  
  Serial.begin(74880);
}

void loop() {

  while (Serial.available() > 0){
     msg_type = Serial.read();
     if (msg_type == 'A'){
       servo1.write( Serial.read() );
     }
     if (msg_type == 'B'){
       servo2.write( Serial.read() );
     }
  }
  
  delay(1);
  
  Serial.print(1023 - analogRead(CURRENT1_PIN));  // the signal is inverted
  Serial.print("\t");
  Serial.println(1023 - analogRead(CURRENT2_PIN));
  
}
