#include <ros.h>
#include <ArduinoHardware.h>
#include <std_msgs/UInt16.h>
#include <Wire.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac1(2); // ADDR pin of MCP4725 connected to Arduino pin 2
Adafruit_MCP4725 dac2(3); // ADDR pin of MCP4725 connected to Arduino pin 3
Adafruit_MCP4725 dac3(4); // ADDR pin of MCP4725 connected to Arduino pin 4
Adafruit_MCP4725 dac4(5); // ADDR pin of MCP4725 connected to Arduino pin 5

int i=1;
ros::NodeHandle nh;

void dac1CB(const std_msgs::UInt16& cmd_msg){
  dac1.setVoltage(cmd_msg.data,false);}
  
void dac2CB(const std_msgs::UInt16& cmd_msg){
  dac2.setVoltage(cmd_msg.data,false);}
  
void dac3CB(const std_msgs::UInt16& cmd_msg){
  dac3.setVoltage(cmd_msg.data,false);} 

ros::Subscriber<std_msgs::UInt16> sub1("dac1", &dac1CB );
ros::Subscriber<std_msgs::UInt16> sub2("dac2", &dac2CB );
ros::Subscriber<std_msgs::UInt16> sub3("dac3", &dac3CB );

void setup(void) {
  Serial.begin(9600);
  Serial.println("Hello!");

  // The begin method must be called with the address of the MCP4725 when ADDR pin is tied to VCC
  // For Adafruit MCP4725A1 this is 0x63
  // For MCP4725A0 this is 0x61
  // For MCP4725A2 this is 0x65
  dac1.begin(0x61);
  dac2.begin(0x61);
  dac3.begin(0x61);
  dac4.begin(0x61); 
  Serial.println("Good Luck");

  nh.initNode();
  nh.subscribe(sub1);
  nh.subscribe(sub2);
  nh.subscribe(sub3);
}

void loop(void)
{
  nh.spinOnce();
  delay(0.1);
}

