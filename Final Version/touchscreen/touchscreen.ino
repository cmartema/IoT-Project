
#include <SPI.h>
#include "Adafruit_GFX.h"
#include <Adafruit_ILI9341.h> // Hardware-specific library
#include <Adafruit_TSC2007.h>
// #include <Adafruit_ImageReader.h>
#include <WiFi.h>
#include <WiFiClient.h>

const char* ssid = "Columbia University";
const char* password ="";
const char* host_ip = "10.206.66.16";
const int port = 50000;

#define STMPE_CS 32
#define TFT_CS   15
#define TFT_DC   33
#define SD_CS    14

// For TSC2007
#define TSC_TS_MINX 300
#define TSC_TS_MAXX 3800
#define TSC_TS_MINY 185
#define TSC_TS_MAXY 3700

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC);
// If you're using the TSC2007 there is no CS pin needed, so instead its an IRQ!
#define TSC_IRQ STMPE_CS
Adafruit_TSC2007 ts = Adafruit_TSC2007();


// Assign human-readable names to some common 16-bit color values:
#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF

#ifndef min
#define min(a, b) (((a) < (b)) ? (a) : (b))
#endif

unsigned long previousMillis = 0;     // will store last time loop was updated
const long interval = 1000;
const int ledPin =  LED_BUILTIN;      // the number of the LED pin
int ledState = LOW;                   // ledState used to set the LED (for debug only)
int codeTimeout = 0;                  // this will be a delay to do something if no keys are pressed
int EEPROMdigit0 = 0;                 // Eprom stored code digit 0
int EEPROMdigit1 = 0;                 // Eprom stored code digit 1
int EEPROMdigit2 = 0;                 // Eprom stored code digit 2
int EEPROMdigit3 = 0;                 // Eprom stored code digit 3
int EEPROMdigit4 = 0;                 // Eprom stored code digit 4
int EEPROMdigit5 = 0;                 // Eprom stored code digit 5


void setup(){
  pinMode(0, OUTPUT);         //for debugging
  Serial.begin(115200);       //enable serial for debugging
  tft.begin();             //Enable display
  ts.begin();              //Touchscreen needs to start
  tft.setRotation(2);      //set screen to prtrait

  //------------------------- setup wifi ----------------------------------------------
  Serial.print("Connecting to ");
  Serial.println(ssid);
  //connect to your WiFi
  WiFi.begin(ssid, password);
  // wait until ESP32 connect to WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected with IP address: ");
  Serial.println(WiFi.localIP());

  //--------------- setup touch field -------------------------
  int X_start = TSC_TS_MINX;
  int X_finish = TSC_TS_MAXX;
  int Y_start = TSC_TS_MINY;
  int Y_finish = TSC_TS_MAXY;

  Serial.print("X_start: ");
  Serial.println(X_start);
  Serial.print("X_finish: ");
  Serial.println(X_finish);
  Serial.print("Y_start: ");
  Serial.println(Y_start);
  Serial.print("Y_finish: ");
  Serial.println(Y_finish);

  keypad();
  loop(); //jump straight into loop

}


void loop() {
  int keypress = 55; //declare integer to store key pressed set at 55 so will only read if a valid number
  int codeArray[] = {0, 0, 0, 0}; // this is where the first 4 key presses will be saved

  //  set human readable touch point limits for key detection

  int presscol1 = 3672;    // start of column 1
  int presscol2 = 2450;   //end of column 1 start of column 2
  int presscol3 = 1350;   //end of column 2 start of column 3
  int presscol4 = 360;   //right most edge of column 3 keys

  int pressrow1 = 3150;    // top start point of row 1
  int pressrow2 = 2374;   //bottom of row 1 top of row 2
  int pressrow3 = 1612;   //bottom of row 2 top of row 3
  int pressrow4 = 895;   //bottom of row 3 start of row 4
  int pressrow5 = 268;

  int keypressIndex = 0;      //array index number

  tft.fillRect(130, 10, 75, 30, BLACK); //clears keypad display area

  delay(800);
  Serial.print("connecting to ");
  Serial.println(host_ip);

  // Use WiFiClient class to create TCP connections  
  WiFiClient client;

  if (!client.connect(host_ip, port)) {
    Serial.println("connection failed");
    delay(500);
    return;
  }

  char mode = '0';
  String send_msg = "";
  String received_msg = "";
  String display_msg;


  //keypad key read loop

  while (1) {
    if (client.available() != 0) {
      Serial.println("Host message is available");
      received_msg = client.readString();
      Serial.print("received message: ");
      Serial.println(received_msg);

      if (received_msg[1] == '0'){
        mode = '0';

        client.print("ack"); // send ack to host
        Serial.println("ack sent");
        
        for (int i = 4; i < received_msg.length(); i++){
          display_msg += received_msg[i];
        }
        
        keypad();
        tft.fillRect(10, 10, 220, 30, BLACK); 
        tft.setTextColor(YELLOW);
        tft.setCursor(10, 10);
        tft.setAddrWindow(10, 10, 220, 30);
        tft.setTextSize(2);
        tft.println(display_msg);
        received_msg = ""; // clear received message
        display_msg = "";
      }
      else {
        if (mode == '0') {
          keypad();
          for (int i = 0; i < keypressIndex; i++) { 
            tft.setTextColor(GREEN); 
            tft.setCursor(130 + 25 * i, 10); 
            tft.setTextSize(4); 
            tft.println(codeArray[i]); 
          }
        }
        mode = '1';

        if (send_msg == "") {
          client.print("ack"); // send ack to host
          Serial.println("ack sent");
        }
        else {
          client.print(send_msg);
          Serial.print("sent message: ");
          Serial.println(send_msg);
          send_msg = "";  // clear send message
        }
        received_msg = ""; // clear received message
      }
    }

    TS_Point null = TS_Point(0, 0, 0);
    if (ts.getPoint() != null && mode == '1') {
      keypress = 11;
      TS_Point p = ts.getPoint();
      bool isAdd = false;
      bool isEnter = false;

      //store pressed key number in 'keypress'
      if (p.x < presscol1 && p.x > presscol2 && p.y < pressrow1 && p.y > pressrow2) keypress = 1;
      if (p.x < presscol2 && p.x > presscol3 && p.y < pressrow1 && p.y > pressrow2) keypress = 2;
      if (p.x < presscol3 && p.x > presscol4 && p.y < pressrow1 && p.y > pressrow2) keypress = 3;

      if (p.x < presscol1 && p.x > presscol2 && p.y < pressrow2 && p.y > pressrow3) keypress = 4;
      if (p.x < presscol2 && p.x > presscol3 && p.y < pressrow2 && p.y > pressrow3) keypress = 5;
      if (p.x < presscol3 && p.x > presscol4 && p.y < pressrow2 && p.y > pressrow3) keypress = 6;

      if (p.x < presscol1 && p.x > presscol2 && p.y < pressrow3 && p.y > pressrow4) keypress = 7;
      if (p.x < presscol2 && p.x > presscol3 && p.y < pressrow3 && p.y > pressrow4) keypress = 8;
      if (p.x < presscol3 && p.x > presscol4 && p.y < pressrow3 && p.y > pressrow4) keypress = 9;

      if (p.x < presscol1 && p.x > presscol2 && p.y < pressrow4 && p.y > pressrow5) {
         isAdd = true;
         keypress = 55;
      }
      if (p.x < presscol2 && p.x > presscol3 && p.y < pressrow4 && p.y > pressrow5) keypress = 0;

      if (p.x < presscol3 && p.x > presscol4 && p.y < pressrow4 && p.y > pressrow5){
        isEnter = true; 
        keypress = 55;
      }
      
      Serial.print("codeArray: ");
      for (int i = 0; i < 4; i++) {
          Serial.print(codeArray[i]);
      }
      Serial.println("");

      if (keypressIndex < 4 && keypress < 10) {
        codeArray[keypressIndex] = keypress;
        keypressIndex++; //increment array index number

        //----------------------------- display keypress ----------------------------------------------
        keypad();
        for (int i = 0; i < keypressIndex; i++) { 
          tft.setTextColor(GREEN); tft.setCursor(130 + 25 * i, 10); 
          tft.setTextSize(4); 
          tft.println(codeArray[i]); 
        }
        delay(300);  //to prevent multiple presses
      }

      //------------------------- clear code -----------------------------------------------
      if (isAdd && keypress == 55) {
        keypressIndex = 0;
        send_msg = "[2] ";
        Serial.println("Add was pressed");
        for(int i = 0; i < 4; i++){
           send_msg += codeArray[i];
        }
        codeArray[0] = 0;
        codeArray[1] = 0;
        codeArray[2] = 0;
        codeArray[3] = 0;
        keypad();
        delay(300);  //to prevent multiple presses
      }
    
      if (isEnter && keypress == 55){
        keypressIndex = 0;
        send_msg = "[1] ";
        Serial.println("Enter was pressed");
        for(int i = 0; i < 4; i++){
           send_msg += codeArray[i];
        }
        codeArray[0] = 0;
        codeArray[1] = 0;
        codeArray[2] = 0;
        codeArray[3] = 0;
        keypad();
        delay(300);  //to prevent multiple presses
      }
    }
  }
  delay(100);
}


void keypad() {
  tft.fillScreen(BLACK);                   //sets screen to black

  tft.drawRect(0, 0, 240, 320, WHITE);     //outline frame of keypad

  tft.drawRect(5, 5, 230, 40, WHITE);      //frame for "user code" and display first 4 keys pressed

  tft.setTextColor(WHITE);                 //write "user code" text into box
  tft.setCursor(10, 15);
  tft.setTextSize(2);
  tft.println("User code:");

  int keyPosX = 5;      //set left hand start point for left column of keys
  int keySpaceX = 5;    //set horizontal space between keys
  int keyPosY = 48;     //set the top most start point for the top row of keys
  int keySpaceY = -5;   //set vertical space between keys (currently not working prpperly for some reason)
  int keyWidth = 73;    //set width of keys
  int keyHieght = 63;   //set hight of keys

  int colum1 = keyPosX;                                   //human readable left start point for left column of keys
  int colum2 = keyPosX + keySpaceX + keyWidth;            //human readable left start point for second column of keys
  int colum3 = keyPosX + (keySpaceX * 2) + (keyWidth * 2);//human readable left start point for third column of keys

  int row1 = keyPosY;                                     //human readable top start point for top row of keys
  int row2 = keyPosY + keySpaceY + keyWidth;              //human readable top start point for second row of keys
  int row3 = keyPosY + (keySpaceY * 2) + (keyWidth * 2);  //human readable top start point for third row of keys
  int row4 = keyPosY + (keySpaceY * 3) + (keyWidth * 3);  //human readable top start point for fourth row of keys


  //================================== draw keys =========================================
  //-----------------------------------key 1 -----------------------------------------
  tft.drawRect(colum1, row1, keyWidth, keyHieght, GREEN); //key 1    draw key
  tft.setTextColor(GREEN);
  tft.setCursor(keyPosX + 25, keyPosY + 15);
  tft.setTextSize(5);
  tft.println("1");
  //-----------------------------------key 2 ----------------------------------------

  tft.drawRect(colum2, row1, keyWidth, keyHieght, GREEN); //key 2
  tft.setTextColor(GREEN);
  tft.setCursor(colum2 + 25, keyPosY + 15);
  tft.setTextSize(5);
  tft.println("2");
  //-----------------------------------key 3 -----------------------------------------

  tft.drawRect(colum3, row1, keyWidth, keyHieght, GREEN); //key 3
  tft.setTextColor(GREEN);
  tft.setCursor(colum3 + 25, keyPosY + 15);
  tft.setTextSize(5);
  tft.println("3");

  //-----------------------------------key 4 --------------------------------------

  tft.drawRect(colum1, row2, keyWidth, keyHieght, GREEN); //key 4
  tft.setTextColor(GREEN);
  tft.setCursor(colum1 + 25, row2 + 15);
  tft.setTextSize(5);
  tft.println("4");

  //-----------------------------------key 5 ------------------------------------

  tft.drawRect(colum2, row2, keyWidth, keyHieght, GREEN); //key 5
  tft.setTextColor(GREEN);
  tft.setCursor(colum2 + 25, row2 + 15);
  tft.setTextSize(5);
  tft.println("5");

  //-----------------------------------key 6 -----------------------------------

  tft.drawRect(colum3, row2, keyWidth, keyHieght, GREEN); //key 6
  tft.setTextColor(GREEN);
  tft.setCursor(colum3 + 25, row2 + 15);
  tft.setTextSize(5);
  tft.println("6");

  //-----------------------------------key 7 ------------------------------------

  tft.drawRect(colum1, row3, keyWidth, keyHieght, GREEN); //key 7
  tft.setTextColor(GREEN);
  tft.setCursor(colum1 + 25, row3 + 15);
  tft.setTextSize(5);
  tft.println("7");

  //-----------------------------------key 8 ----------------------------------

  tft.drawRect(colum2, row3, keyWidth, keyHieght, GREEN); //key 8
  tft.setTextColor(GREEN);
  tft.setCursor(colum2 + 25, row3 + 15);
  tft.setTextSize(5);
  tft.println("8");

  //-----------------------------------key 9 --------------------------------

  tft.drawRect(colum3, row3, keyWidth, keyHieght, GREEN); //key 9
  tft.setTextColor(GREEN);
  tft.setCursor(colum3 + 25, row3 + 15);
  tft.setTextSize(5);
  tft.println("9");

  //-----------------------------------key A -------------------------------

  tft.drawRect(colum1, row4, keyWidth, keyHieght, GREEN); //key A
  tft.setTextColor(GREEN);
  tft.setCursor(colum1 + 25, row4 + 15);
  tft.setTextSize(5);
  tft.println("A");

  //-----------------------------------key 0 -------------------------------

  tft.drawRect(colum2, row4, keyWidth, keyHieght, GREEN); //key 0
  tft.setTextColor(GREEN);
  tft.setCursor(colum2 + 25, row4 + 15);
  tft.setTextSize(5);
  tft.println("0");

  //-----------------------------------key E -------------------------------

  tft.drawRect(colum3, row4, keyWidth, keyHieght, GREEN); //key E
  tft.setTextColor(GREEN);
  tft.setCursor(colum3 + 25, row4 + 15);
  tft.setTextSize(5);
  tft.println("E");
}
