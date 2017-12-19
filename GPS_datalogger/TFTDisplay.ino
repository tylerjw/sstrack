#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7735.h> // Hardware-specific library

// 0 - vertical pins down
// 1 - horizontal pins right
// 2 - vertical pins up
// 3 - horizontal pins left
const int tft_rotation = 3;

float knotsToMph(float knots) { return knots*1.15078; }
float knotsToMps(float knots) { return knots*0.5144447; }
float knotsToKph(float knots) { return knots*1.852001; }

void drawStats(Adafruit_ST7735 &tft, Adafruit_GPS &gps) {
  char line[14]; // horizontal line on tft display is 13 characters

  tft.setRotation(tft_rotation);
  tft.setCursor(0,0);
  tft.setTextSize(2);
  tft.setTextColor(ST7735_BLUE);
  sprintf(line, "%02d/%02d/20%02d", gps.month, gps.day, gps.year);
  tft.println(line);
  sprintf(line, "%02d:%02d:%02d.%03d", gps.hour, gps.minute, gps.seconds, gps.milliseconds);
  tft.println(line);
  tft.setTextColor(ST7735_RED);
  sprintf(line, "% 3dmph % 3ddeg", knotsToMph(gps.speed), gps.angle);
  tft.println(line);
}
