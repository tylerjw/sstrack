
float knotsToMph(float knots) { return knots*1.15078; }
float knotsToMps(float knots) { return knots*0.5144447; }
float knotsToKph(float knots) { return knots*1.852001; }

double mToMi(double m) { return m*0.000621371; }

void gpsScanMode() {
  // set gps to 1Hz mode and output rmc and gga
  gps.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  gps.sendCommand(PMTK_API_SET_FIX_CTL_1HZ);
  gps.sendCommand(PMTK_SET_NMEA_UPDATE_200_MILLIHERTZ);
  gps.waitForSentence("$PMTK001,314,3*36");
  gps.waitForSentence("$PMTK001,300,3*33");
  gps.waitForSentence("$PMTK001,220,3*30");
}

void gpsCaptureMode() {
  gps.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  gps.sendCommand(PMTK_API_SET_FIX_CTL_10HZ);
  gps.sendCommand(PMTK_SET_NMEA_UPDATE_10HZ);
  gps.waitForSentence("$PMTK001,314,3*36");
  gps.waitForSentence("$PMTK001,300,3*33");
  gps.waitForSentence("$PMTK001,220,3*30");
}

double distanceBetween(double lat1, double long1, double lat2, double long2)
{
  // returns distance in meters between two positions, both specified
  // as signed decimal-degrees latitude and longitude. Uses great-circle
  // distance computation for hypothetical sphere of radius 6372795 meters.
  // Because Earth is no exact sphere, rounding errors may be up to 0.5%.
  // Courtesy of Maarten Lamers
  double delta = radians(long1-long2);
  double sdlong = sin(delta);
  double cdlong = cos(delta);
  lat1 = radians(lat1);
  lat2 = radians(lat2);
  double slat1 = sin(lat1);
  double clat1 = cos(lat1);
  double slat2 = sin(lat2);
  double clat2 = cos(lat2);
  delta = (clat1 * slat2) - (slat1 * clat2 * cdlong);
  delta = sq(delta);
  delta += sq(clat2 * sdlong);
  delta = sqrt(delta);
  double denom = (slat1 * slat2) + (clat1 * clat2 * cdlong);
  delta = atan2(delta, denom);
  return delta * 6372795;
}
