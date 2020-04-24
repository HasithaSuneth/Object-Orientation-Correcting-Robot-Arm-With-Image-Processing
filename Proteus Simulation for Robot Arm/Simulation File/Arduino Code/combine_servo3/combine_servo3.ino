// 2 stepper motors used for move up-down & left-right
#include <Servo.h> 
 
Servo upDownServo;  
Servo rotateServo;
Servo grabServo;
 
#define side_dir 5
#define side_step 6
#define up_dir 7
#define up_step 8
#define Revolution 200

int strrotatepos = 0;
int rotatepos;
int strgrabpos = 0;
int grabpos = 90;
int orientation =0;
const int center = 2; 
const int side = 3; 
const int up = 4;

void setup() 
{ 
  pinMode(center, INPUT);
  pinMode(side, INPUT);
  pinMode(side_dir, OUTPUT);
  pinMode(side_step, OUTPUT);
  pinMode(up_dir, OUTPUT);
  pinMode(up_step, OUTPUT);
  rotateServo.attach(10);
  grabServo.attach(11);
  Serial.begin(9600); 
  start_position();
} 
 
 
void loop() 
{ 
  side_position();  // Set arm at default position
  serial_get();   // Wait for serial input
  rotatepos = (orientation/2);  //change value according to servo duty cycle
  delay(100);
  center_position();  // move arm to center
  next_position(grabpos); // move arm down, grab object & move arm up
  delay(2000);
  rotate_position();  // correct orientation of the object
  delay(2000);
  next_position(strgrabpos);  // Move arm down, release object & move arm up
  delay(1000);
  start_position();   // confirmed arm at default position
  delay(2000);
  Serial.print("complete"); 
} 

void side_position(){
  if (digitalRead(center)==HIGH || digitalRead(side)!=HIGH){
    digitalWrite(side_dir, HIGH);
    while (digitalRead(side) == HIGH){
      digitalWrite(side_step, HIGH);
      delayMicroseconds(1000);
      digitalWrite(side_step, LOW);
      delayMicroseconds(1000);
    }
  }
}

void center_position(){
  if (digitalRead(side)==HIGH || digitalRead(center)!=HIGH){
    digitalWrite(side_dir, LOW);
    while (digitalRead(center) == HIGH){
      digitalWrite(side_step, HIGH);
      delayMicroseconds(1000);
      digitalWrite(side_step, LOW);
      delayMicroseconds(1000);
    }
  }
}

void start_position(){
  if (digitalRead(up)!=HIGH){
    digitalWrite(up_dir, LOW);
    while (digitalRead(up) == HIGH){
      digitalWrite(up_step, HIGH);
      delayMicroseconds(1000);
      digitalWrite(up_step, LOW);
      delayMicroseconds(1000);
    }
  }
  grabServo.write(strgrabpos);   
  rotateServo.write(strrotatepos);
}

void rotate_position(){
  rotateServo.write(rotatepos);
}

void next_position(int x){
  digitalWrite(up_dir, HIGH); // go to down
  for(int i=0; i<3*Revolution; i++){
    digitalWrite(up_step, HIGH);
    delayMicroseconds(1000);
    digitalWrite(up_step, LOW);
    delayMicroseconds(1000);
  }
  grabServo.write(x);   // need to add delay for grab cup
  delay(1000);
  digitalWrite(up_dir, LOW);  // go to up
  for(int i=0; i<3*Revolution; i++){
    digitalWrite(up_step, HIGH);
    delayMicroseconds(1000);
    digitalWrite(up_step, LOW);
    delayMicroseconds(1000);
  }
}

void serial_get(){
  while(1){
    if (Serial.available()>0){  // Wait for signal from Raspberry pi
      int SerInt=Serial.parseInt(); 
      if (SerInt != 0){         // Confirm recieved data
        Serial.print(SerInt);
        orientation = SerInt;
        SerInt=0;
        break;
      }
    }
  }
}
