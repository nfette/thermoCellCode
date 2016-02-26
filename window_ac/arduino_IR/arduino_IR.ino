/*
thermoCellCode/window_ac/arduino_IR: 
   Translate commands from serial to the window AC unit,
   acknowledge back to serial.
   The commands are pre-programmed in the header file.
   An IR LED must be connected on pin 3.
   Requires the IRremote library by Ken Shirriff. http://arcfn.com
   (This must replace the RobotIRremote library included by default.)
   Created by Nicholas Fette, 2016-02-02.

Recent changes:
2016-02-05 nfette Added two relay control signals.
*/

#include <IRremote.h>
#include "my_ac_remote_codes.h"

int RECV_PIN = 10;
int SEND_PIN = 3;
// Do not use pin 13 for relays since it 'beeps' on boot.
int RELAYA_PIN = 11;
int RELAYB_PIN = 12;

IRrecv irrecv(RECV_PIN);
IRsend irsend;

decode_results results;
bool verbose;

void setup()
{
  Serial.begin(9600);
  //irrecv.enableIRIn(); // Start the receiver
  pinMode(RELAYA_PIN, OUTPUT);
  pinMode(RELAYB_PIN, OUTPUT);
  verbose = false;
}

void loop() {
  static int msg;
  int codeLen = 32;
  if (Serial.available()) {
    msg = Serial.read();
    switch (msg) {
      case 'p':
        irsend.sendNEC(ACCODE_POWER, codeLen);
        if (verbose)
          Serial.println("Sent power");
        delay(1000);
        break;
      case 'u':
        irsend.sendNEC(ACCODE_TEMPUP, codeLen);
        if (verbose)
          Serial.println("Sent tempup");
        standardPause();
        break;
      case 'd':
        irsend.sendNEC(ACCODE_TEMPDOWN, codeLen);
        if (verbose)
          Serial.println("Sent temp down");
        standardPause();
        break;
      case 'f':
        irsend.sendNEC(ACCODE_FAN, codeLen);
        if (verbose)
          Serial.println("Sent AC toggle fan.");
        standardPause();
        break;
      case 'm':
        irsend.sendNEC(ACCODE_MODE, codeLen);
        if (verbose)
          Serial.println("Sent A/C mode.");
        standardPause();
        break;
      case 't':
        irsend.sendNEC(ACCODE_TIMER, codeLen);
        if (verbose)
          Serial.println("Sent timer.");
        standardPause();
        break;
      case 'a':
        digitalWrite(RELAYA_PIN, HIGH);
        if (verbose)
          Serial.println("Sent 'on' to relay A.");
        break;
      case 'b':
        digitalWrite(RELAYB_PIN, HIGH);
        if (verbose)
          Serial.println("Sent 'on' to relay B.");
        break;
      case 'A':
        digitalWrite(RELAYA_PIN, LOW);
        if (verbose)
          Serial.println("Sent 'off' to relay A.");
        break;
      case 'B':
        digitalWrite(RELAYB_PIN, LOW);
        if (verbose)
          Serial.println("Sent 'off' to relay B.");
        break;
      case 'v':
        verbose = false;
        Serial.println("Set verbose = false.");
        break;
      case 'V':
        verbose = true;
        Serial.println("Set verbose = true.");
        break;
      case '?':
        Serial.print("Relay A is ");
        if (digitalRead(RELAYA_PIN))
          Serial.print("on");
        else
          Serial.print("off");
        Serial.print(" and Relay B is ");
        if (digitalRead(RELAYB_PIN))
          Serial.println("on.");
        else
          Serial.println("off.");
        break;
      default:
        Serial.print("Unrecognized ascii code: ");
        Serial.print(msg);
        Serial.println(". Try one of [pmftudaAbBvV?].");
    }
  }
}

void standardPause() {
  delay(100);
}

void practiceLoop() {
  int codeLen = 32;
  irsend.sendNEC(ACCODE_POWER, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_TEMPUP, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_TEMPUP, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_TEMPDOWN, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_TEMPDOWN, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_FAN, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_FAN, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_FAN, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_MODE, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_MODE, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_TIMER, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_TIMER, codeLen);
  delay(10*1000);
  irsend.sendNEC(ACCODE_POWER, codeLen);
  delay(10*1000);
}


void receiveLoop() {
  if (irrecv.decode(&results)) {
    switch (results.value) {
      case ACCODE_POWER:
        Serial.println("POWER");
        break;
      case ACCODE_TEMPUP:
        Serial.println("TEMPUP");
        break;
      case ACCODE_TEMPDOWN:
        Serial.println("TEMPDOWN");
        break;
      case ACCODE_FAN:
        Serial.println("FAN");
        break;
      case ACCODE_TIMER:
        Serial.println("TIMER");
        break;
      case ACCODE_MODE:
        Serial.println("MODE");
        break;
      case ACCODE_REPEAT:
        Serial.println("REPEAT");
        break;
      default:
        Serial.println(results.value, HEX);
        break;
    }

    irrecv.resume(); // Receive the next value
  }
  delay(100);
}
