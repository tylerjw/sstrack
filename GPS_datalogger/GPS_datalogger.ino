// This code was written for use with feather m0 adalogger and feather gps for logging gps data to file
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#include <Adafruit_GPS.h>
#include <SPI.h>
#include <SD.h>

// what's the name of the hardware serial port?
#define GPSSerial Serial1

// Connect to the gps on the hardware port
Adafruit_GPS gps(&GPSSerial);

// Set GPSECHO to 'false' to turn off echoing the gps data to the Serial console
// Set to 'true' if you want to debug and listen to the raw gps sentences
#define GPSECHO false

//uint32_t timer = millis();

#define PMTK_SET_NMEA_OUTPUT_RMCGGA5 "$PMTK314,0,1,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*2C"
#define PMTK_Q_NAV_THRESHOLD "$PMTK447*35"
#define PMTK_SET_NAV_SPEED_1MS "$PMTK386,1.0*3C"
#define PMTK_SET_NAV_SPEED_2MS "$PMTK386,2.0*3F"
#define PMTK_SET_BAUD_115200 "$PMTK251,115200*1F"
#define PMTK_API_SET_FIX_CTL_10HZ "$PMTK300,100,0,0,0,0*2C"

const int chipSelect = 4;
bool fileOpen = false;
File dataFile;

const short num_button_pins = 3;
const short button_pins[num_button_pins] = {9, 10, 11};

const int fileLed = 5;
const int calLed = 6;

Adafruit_BNO055 bno = Adafruit_BNO055();
adafruit_bno055_offsets_t CalData;

const float p = 3.1415926;
static double tripDistance = 0.0; // miles

void setup()
{
  //while (!Serial);  // uncomment to have the sketch wait until Serial is ready

  // connect at 115200 so we can read the gps fast enough and echo without dropping chars
  // also spit it out
  Serial.begin(115200);

  // Initialize gps
  // 9600 NMEA is the default baud rate for Adafruit MTK gps's- some use 4800
//  gps.begin(9600);
  gps.begin(115200);

  // set the baud rate at 115200
//  gps.sendCommand(PMTK_SET_BAUD_115200);

  gpsScanMode();

  // RMC every fix, GGA every 5 fixes
  //gps.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA5);

  // Request updates on antenna status, comment out to keep quiet
  gps.sendCommand(PGCMD_NOANTENNA);

  // set the nav threshold to 1ms so the gps won't generate new points if the speed is low
  gps.sendCommand(PMTK_SET_NAV_SPEED_1MS);

  delay(1000);

  // Initialize SD card
  while (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present... trying again.");
    delay(1000);
  }

  // setup bno
  if (!bno.begin()) {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }
  LoadBNO055Calibration(bno);
  bno.setExtCrystalUse(true);

  // setup LEDs
  pinMode(fileLed, OUTPUT);
  digitalWrite(fileLed, LOW);
  pinMode(calLed, OUTPUT);
  digitalWrite(calLed, LOW);

  // setup buttons
  for(short i=0; i < num_button_pins; i++) {
    pinMode(button_pins[i], INPUT_PULLUP);
  }

  // Use this initializer if you're using a 1.8" TFT
  initTft();
}

void loop() // run over and over again
{
  char datestamp[7];
  char timestamp[11];
  char gyroLine[53];
  char eulerLine[54];

  // read data from the gps in the 'main loop'
  char c = gps.read();
  // if you want to debug, this is a good time to do it!
  if (GPSECHO)
    if (c) Serial.print(c);
  // if a sentence is received, we can check the checksum, parse it...
  if (gps.newNMEAreceived()) {
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data

    gps.parse(gps.lastNMEA());

    sprintf(datestamp, "%02d%02d%02d", gps.year, gps.month, gps.day);
    sprintf(timestamp, "%02d%02d%02d.%03d", gps.hour, gps.minute, gps.seconds, gps.milliseconds);

    imu::Vector<3> gyro = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
    sprintf(gyroLine, "$GYRO,%s,%s,%+.3f,%+.3f,%+.3f\r\n", datestamp, timestamp, gyro.x(), gyro.y(), gyro.z());

    sensors_event_t event;
    sprintf(timestamp, "%02d%02d%02d.%03d", gps.hour, gps.minute, gps.seconds, gps.milliseconds);
    bno.getEvent(&event);
    sprintf(eulerLine, "$EULER,%s,%s,%+.3f,%+.3f,%+.3f\r\n", datestamp, timestamp, event.orientation.x, event.orientation.y, event.orientation.z);

    // fix whitespace issue with how NMEA strings are stored
    String nmeaLine(gps.lastNMEA());
    nmeaLine.trim();
    nmeaLine += "\r\n";

    if (fileOpen) {
      dataFile.print(nmeaLine);
      dataFile.print(gyroLine);
      dataFile.print(eulerLine);
      dataFile.flush();

      // cal LED
      if (bno.isFullyCalibrated()) {
        digitalWrite(calLed, HIGH);
      } else {
        digitalWrite(calLed, LOW);
      }
    } else {
      drawStats(gps, bno);

      // gps fix LED
      if (gps.fix) {
        digitalWrite(calLed, HIGH);
      } else {
        digitalWrite(calLed, LOW);
      }
    }
  }

  int buttonState = handleButtons(button_pins, num_button_pins);
  if (buttonState != 0) {
    // button pressed
    if (buttonState == 1) {
      if (fileOpen) {
        // change gps mode
        gpsScanMode();

        // clear screen
        clearScreen();

        // close the file
        dataFile.close();
        Serial.println("Stopping the Log");
        digitalWrite(fileLed, LOW);
        fileOpen = false;
      } else {
        // change gps mode
        gpsCaptureMode();

        // clear screen
        clearScreen();
        drawRecordingMessage();

        // open the file
        String filename = nextFilename("/", "SST", "LOG");
        dataFile = SD.open(filename, FILE_WRITE);
        Serial.println("Starting the Log " + filename);
        digitalWrite(fileLed, HIGH);
        fileOpen = true;
      }
    } else if (buttonState == 2) {
      ClearBNO055Cal();
      digitalWrite(calLed, LOW);
      LoadBNO055Calibration(bno);
    }
  }
}
