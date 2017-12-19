char FileNameCalib[] = "CalFile.DAT";

size_t readField(File* file, char* str, size_t size, char* delim) {
  char ch;
  size_t n = 0;
  while ((n + 1) < size && file->read(&ch, 1) == 1) {
    // ignore CR or NL or tabs.
    if ((ch == '\r') || (ch == '\n') || (ch == '\t')) { continue; }
    if (strchr(delim, ch)) { break; }
    str[n++] = ch;
  }
  str[n] = '\0';
  return n;
}

void WriteBNO055Offsets(char* filename, adafruit_bno055_offsets_t* V, bool Append) {

  File ThisFile = SD.open(filename, FILE_WRITE);
  if (ThisFile) {
    if (!Append) { ThisFile.seek(0); }

    uint16_t* p = &(V->accel_offset_x);
    for (int i = 0; i<11; i++) {
      ThisFile.print((int16_t)*(p + i));  ThisFile.print(",\t ");
      //Serial.print("\n");Serial.print((int16_t)*(p + i));    Serial.print("  ");
    }
    //ThisFile.println(" * ");
    //Serial.println(" * ");
    ThisFile.close();
  }
}

void ReadBNO055Offsets(char* filename, adafruit_bno055_offsets_t* V) {
  char buffer[25];
  bool ReadStatus = false;
 //Serial.println("in Read Offsets");

  File ThisFile = SD.open(filename, FILE_READ);
  if (ThisFile) {
    uint16_t* p = &(V->accel_offset_x);
    for (int i = 0; i<11; i++) {
      int Value = 0;
      int n = readField(&ThisFile, buffer, 25, ",;\n");
      if (n) { Value = atoi(buffer); }

      *(p + i) = Value;
      Serial.print(i); Serial.print(" "); Serial.print(buffer); Serial.print("  "); Serial.println(Value);
    }
    ReadStatus = true;
    ThisFile.close();
    //Serial.println(" * ");
    

    //return V=Value;
  }
  else { Serial.println("ReadBNO055Offsets : Cannot open the specified file"); }
}

void RestoreSensorOffsets(Adafruit_BNO055 &bno) {
  ReadBNO055Offsets(FileNameCalib, &CalData);
  bno.setSensorOffsets(CalData);
}

bool SaveSensorOffsets(Adafruit_BNO055 &bno) {
  bool mystatus = bno.getSensorOffsets(CalData);
  if (mystatus) {
    WriteBNO055Offsets(FileNameCalib, &CalData, false);      // this is the single set of offset data that are read in the Restore routine
  }
  return mystatus;
}

/**************************************************************************/
/*
    Display the raw calibration offset and radius data
    */
/**************************************************************************/
void displaySensorOffsets(const adafruit_bno055_offsets_t &calibData)
{
    Serial.print("\nAccelerometer: ");
    Serial.print(calibData.accel_offset_x); Serial.print(" ");
    Serial.print(calibData.accel_offset_y); Serial.print(" ");
    Serial.print(calibData.accel_offset_z); Serial.print(" ");

    Serial.print("\nGyro: ");
    Serial.print(calibData.gyro_offset_x); Serial.print(" ");
    Serial.print(calibData.gyro_offset_y); Serial.print(" ");
    Serial.print(calibData.gyro_offset_z); Serial.print(" ");

    Serial.print("\nMag: ");
    Serial.print(calibData.mag_offset_x); Serial.print(" ");
    Serial.print(calibData.mag_offset_y); Serial.print(" ");
    Serial.print(calibData.mag_offset_z); Serial.print(" ");

    Serial.print("\nAccel Radius: ");
    Serial.print(calibData.accel_radius);

    Serial.print("\nMag Radius: ");
    Serial.print(calibData.mag_radius);
    Serial.print("\n");
}

void ClearBNO055Cal() {
  SD.remove(FileNameCalib);
}

void LoadBNO055Calibration(Adafruit_BNO055 &bno) { 
  if (!SD.exists(FileNameCalib)) { //if file does not exist create one 
    Serial.println("\nNo Calibration Data for this sensor exists");
        sensors_event_t event;
        bno.getEvent(&event);
          while (!bno.isFullyCalibrated())    // Calibration method from the Data sheet 
            {
              bno.getEvent(&event);
              Serial.print("\nX: "); Serial.print(event.orientation.x, 4);
              Serial.print("\tY: "); Serial.print(event.orientation.y, 4);
              Serial.print("\tZ: "); Serial.print(event.orientation.z, 4);
              displayCalStatus(bno);
              delay(500);
            }
        SaveSensorOffsets(bno);  //offset data sved to file 
        bno.getSensorOffsets(CalData);  //checking the data (debugging) 
        displayCalStatus(bno);             //checking the data (debugging)
        displaySensorOffsets(CalData);  //checking the data (debugging)
        
          if (SD.exists(FileNameCalib) && bno.isFullyCalibrated()) {
            Serial.print("\nCalibration File Saved\n\n"); //checking the data (debugging)
          }else{
            Serial.print("\nFile Saving Error\n");        //checking the data (debugging)
            }
    delay(100);
  }else{
    Serial.print(F("\n\nCalibration Data Found\n"));  //Clibration data exist already 
    
    RestoreSensorOffsets(bno); //restore the data onto the sensor 
    bno.getSensorOffsets(CalData);  //checking the data (debugging)
    displaySensorOffsets(CalData);  //checking the data (debugging)
  
  delay(3000);
  }
}
