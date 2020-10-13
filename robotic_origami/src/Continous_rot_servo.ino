#include <Servo.h> //Servo library
#include <ros.h>
#include <std_msgs/UInt16.h>
#include <Arduino.h>

ros::NodeHandle  nh;
Servo myservo;  //Servo name is myservo
int pos; 
void servo_cb( const std_msgs::UInt16& cmd_msg){

   while(pos<=cmd_msg.data)  // goes from 0 degrees to 180 degrees 
  {                                  // in steps of 1 degree 
    myservo.write(pos);
    pos = pos+1;    // tell servo to go to position in variable 'pos' 
    delay(50);                       // waits 15ms for the servo to reach the position 
  } 
   while(pos>=cmd_msg.data)    // goes from 180 degrees to 0 le 
  {                                
    myservo.write(pos); 
    pos = pos-1;    // tell servo to go to position in variable 'pos' 
    delay(50);                       // waits 15ms for the servo to reach the position 
  }   
  //myservo.write(cmd_msg.data); 
  //delay(1000);
  nh.loginfo("Program info");}

ros::Subscriber<std_msgs::UInt16> sub("servo", servo_cb);

void setup() {
  
  ///.Serial.begin(9600);
  nh.initNode();
  nh.subscribe(sub);  
  myservo.attach(9);  // attaches the servo signal pin on pin D6

}

void loop() {
  nh.spinOnce();
  delay(1);    
}
