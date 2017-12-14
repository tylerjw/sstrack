// This code was written for use with feather m0 adalogger and feather gps for logging gps data to file
     
#include <Adafruit_GPS.h>
#include <SPI.h>
#include <SD.h>

// what's the name of the hardware serial port?
#define GPSSerial Serial1

// Connect to the GPS on the hardware port
Adafruit_GPS GPS(&GPSSerial);
     
// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences
#define GPSECHO false

//uint32_t timer = millis();

#define PMTK_SET_NMEA_OUTPUT_RMCGGA5 "$PMTK314,0,1,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*2C"

const int chipSelect = 4;
bool fileOpen = false;
File dataFile;

const int startStopButton = 10;
#define LONG_PRESS 1
#define SHORT_PRESS 2

const int statusLed = 5;

void setup()
{
  //while (!Serial);  // uncomment to have the sketch wait until Serial is ready

  // connect at 115200 so we can read the GPS fast enough and echo without dropping chars
  // also spit it out
  Serial.begin(115200);
  Serial.println("Adafruit GPS library basic test!");

  // Initialize GPS
  // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
  GPS.begin(57600);

  // set the baud rate at 57600
//  GPS.sendCommand(PMTK_SET_BAUD_57600);
//  GPS.begin(57600);

  // increase the fix and output rate to 5Hz
  GPS.sendCommand(PMTK_API_SET_FIX_CTL_5HZ);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_5HZ);
  
  // RMC every fix, GGA every 5 fixes
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA5);
     
  // Request updates on antenna status, comment out to keep quiet
  GPS.sendCommand(PGCMD_NOANTENNA);

  delay(1000);

  // Initialize SD card
  while (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present... trying again.");
    delay(1000);
  }

  // setup fileOpen LED
  pinMode(statusLed, OUTPUT);
  digitalWrite(statusLed, LOW);

  // setup start/stop button
  pinMode(startStopButton, INPUT_PULLUP);
}

void loop() // run over and over again
{
  // read data from the GPS in the 'main loop'
  char c = GPS.read();
  // if you want to debug, this is a good time to do it!
  if (GPSECHO)
    if (c) Serial.print(c);
  // if a sentence is received, we can check the checksum, parse it...
  if (GPS.newNMEAreceived()) {
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
    
    GPS.parse(GPS.lastNMEA());
    
    if (fileOpen) {
      dataFile.print(GPS.lastNMEA());
      dataFile.flush();
//      Serial.print(GPS.lastNMEA());
    }
  }

  // if millis() or timer wraps around, we'll just reset it
  //  if (timer > millis()) timer = millis();

  int buttonState = handleButton(startStopButton);
  if (buttonState == LONG_PRESS) {
//    Serial.println("LONG PRESS");
    if (fileOpen) {
      // close the file
      dataFile.close();
      Serial.println("Stopping the Log");
      digitalWrite(statusLed, LOW);
      fileOpen = false;
    } else {
      // open the file
      String filename = nextFilename("/", "SST", "LOG");
      dataFile = SD.open(filename, FILE_WRITE);
      Serial.println("Starting the Log " + filename);
      digitalWrite(statusLed, HIGH);
      fileOpen = true;
    }
  }
//  if (buttonState == SHORT_PRESS) {
//    Serial.println("SHORT PRESS");
//  }
  
}
