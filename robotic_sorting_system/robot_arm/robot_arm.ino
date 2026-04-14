#include <Servo.h>

Servo baseServo;
Servo shoulderServo;
Servo elbowServo;
Servo gripperServo;

// Initial positions (Home state)
const int baseHome = 90;
const int shoulderHome = 90;
const int elbowHome = 90;
const int gripperOpen = 90;
const int gripperClose = 10;

// Shared Drop Position
const int baseDrop = 0;       
const int shoulderDrop = 120;
const int elbowDrop = 120;

void setup() {
  Serial.begin(9600);
  
  // Attach servos to specified pins
  baseServo.attach(3);
  shoulderServo.attach(5);
  elbowServo.attach(6);
  gripperServo.attach(9);
  
  // Start at home position
  goHome();
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // Clean up newline characters or spaces
    
    bool validCommand = false;
    
    if (cmd == "L") {
      pick_left();
      validCommand = true;
    } else if (cmd == "C") {
      pick_center();
      validCommand = true;
    } else if (cmd == "R") {
      pick_right();
      validCommand = true;
    }
    
    if (validCommand) {
      // Ensure smooth operation by proceeding to drop and reset
      drop_object();
      goHome();
    }
  }
}

// Function to move servo safely and smoothly
void moveSlowly(Servo &servo, int targetPos) {
  int currentPos = servo.read();
  if (currentPos < targetPos) {
    for (int p = currentPos; p <= targetPos; p++) {
      servo.write(p);
      delay(15);
    }
  } else {
    for (int p = currentPos; p >= targetPos; p--) {
      servo.write(p);
      delay(15);
    }
  }
}

// Moves arm to a safe starting state
void goHome() {
  gripperServo.write(gripperOpen);
  moveSlowly(elbowServo, elbowHome);
  moveSlowly(shoulderServo, shoulderHome);
  moveSlowly(baseServo, baseHome);
  delay(200);
}

// Sequence to pick object from the left
void pick_left() {
  moveSlowly(baseServo, 135); // Move to Left
  delay(200);
  
  moveSlowly(shoulderServo, 45); // Extend shoulder
  moveSlowly(elbowServo, 45);    // Extend elbow
  delay(500);
  
  gripperServo.write(gripperClose); // Grab object
  delay(500);
  
  moveSlowly(shoulderServo, shoulderHome); // Lift arm structure up before moving
  moveSlowly(elbowServo, elbowHome);
}

// Sequence to pick object from the center
void pick_center() {
  moveSlowly(baseServo, 90); // Move to Center
  delay(200);
  
  moveSlowly(shoulderServo, 45); // Extend shoulder
  moveSlowly(elbowServo, 45);    // Extend elbow
  delay(500);
  
  gripperServo.write(gripperClose); // Grab object
  delay(500);
  
  moveSlowly(shoulderServo, shoulderHome); // Lift arm structure up before moving
  moveSlowly(elbowServo, elbowHome);
}

// Sequence to pick object from the right
void pick_right() {
  moveSlowly(baseServo, 45); // Move to Right
  delay(200);
  
  moveSlowly(shoulderServo, 45); // Extend shoulder
  moveSlowly(elbowServo, 45);    // Extend elbow
  delay(500);
  
  gripperServo.write(gripperClose); // Grab object
  delay(500);
  
  moveSlowly(shoulderServo, shoulderHome); // Lift arm structure up before moving
  moveSlowly(elbowServo, elbowHome);
}

// Drops object into the bucket
void drop_object() {
  moveSlowly(baseServo, baseDrop); // Position for Drop
  delay(200);
  
  moveSlowly(shoulderServo, shoulderDrop);
  moveSlowly(elbowServo, elbowDrop);
  delay(500);
  
  
  gripperServo.write(gripperOpen); // Release object
  delay(500);
}
