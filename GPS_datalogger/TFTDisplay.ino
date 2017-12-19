#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7735.h> // Hardware-specific library

#define TFT_CS     19
#define TFT_RST    16  // you can also connect this to the Arduino reset
                       // in which case, set this #define pin to -1!
#define TFT_DC     17
Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS,  TFT_DC, TFT_RST);

// 0 - vertical pins down
// 1 - horizontal pins right
// 2 - vertical pins up
// 3 - horizontal pins left
const int tft_rotation = 3;

void initTft() {
  tft.initR(INITR_BLACKTAB);   // initialize a ST7735S chip, black tab
  clearScreen();
}

void clearScreen() {
  tft.fillScreen(ST7735_BLACK);
}

void drawStats(Adafruit_GPS &gps, Adafruit_BNO055 &bno) {
  char line[24]; // horizontal line on tft display is 13 characters

  tft.setRotation(tft_rotation);
  tft.setCursor(0,0);
  tft.setTextSize(2);
  tft.setTextColor(ST7735_BLUE, ST7735_BLACK);
  sprintf(line, "%02d/%02d/20%02d", gps.month, gps.day, gps.year);
  tft.println(line);
  // sprintf(line, "%02d:%02d:%02d", gps.hour, gps.minute, gps.seconds);
  // tft.println(line);
  // tft.setTextColor(ST7735_RED, ST7735_BLACK);
  // sprintf(line, "%03dmph %03ddeg", knotsToMph(gps.speed), gps.angle);
  // tft.println(line);
  sprintf(line, "fix: %d (%d)", gps.fixquality, gps.satellites);
  tft.println(line);
  tft.println("-------------");

  tft.setTextColor(ST7735_YELLOW, ST7735_BLACK);
  imu::Vector<3> gyro = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  tft.println("GYRO (x,y,z)");
  sprintf(line, "%3d %3d %3d", int(gyro.x()), int(gyro.y()), int(gyro.z()));
  tft.println(line);
  sensors_event_t event;
  bno.getEvent(&event);
  tft.println("EULER (x,y,z)");
  sprintf(line, "%3d %3d %3d",
          int(event.orientation.x), int(event.orientation.y), int(event.orientation.z));
  tft.println(line);
  {
    tft.setTextSize(1);
    uint8_t system, gyro, accel, mag;
    system = gyro = accel = mag = 0;
    bno.getCalibration(&system, &gyro, &accel, &mag);
    sprintf(line, "Cal: S:%d G:%d A:%d M:%d", system, gyro, accel, mag);
    tft.println(line);
  }
}

void drawRecordingMessage() {
  tft.setRotation(tft_rotation);
  tft.setCursor(0,30);
  tft.setTextSize(3);
  tft.setTextColor(ST7735_GREEN, ST7735_BLACK);
  tft.println("Logging");
}
