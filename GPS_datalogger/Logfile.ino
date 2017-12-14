String nextFilename(char* dir, char* base, char* ext) {
  SD.open(dir);
  char filename[13];
  for(int i = 0; i < 9999; i++) {
    sprintf(filename, "%s%04d.%s", base, i, ext);
//    Serial.println("testing filename: " + String(filename));
    if (! SD.exists(filename)) {
      return String(filename);
    }
  }
}

