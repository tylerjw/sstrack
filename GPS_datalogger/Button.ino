// copy to main file for use
#define NO_CHANGE 0
#define LONG_PRESS 1
#define SHORT_PRESS 2

int handleButton(int pin)
{
  static long button_timer = 0;
  static const long longpress_time = 500;
  static const long shortpress_time = 50;

  static boolean button_active = false;
  static boolean longpress_active = false;

  int ret = NO_CHANGE;
  
  if(digitalRead(pin) == LOW) {
    // button pressed

    if (button_active == false) {
      button_active = true;
      button_timer = millis();
    }

    if ((millis() - button_timer > longpress_time) && (longpress_active == false)) {
      longpress_active = true;
      ret = LONG_PRESS;
    }
  } else {
    // button not pressed

    if(button_active == true) {
      if(longpress_active == true) {
        longpress_active = false;
      } else if(millis() - button_timer > shortpress_time) {
        ret = SHORT_PRESS;
      }
      button_active = false;
    }
  }

  return ret;
}

short handleButtons(const short pins[], const short len)
{
  static long button_timer = 0;
  static const long min_press_time = 25;
  static boolean button_active = false;
  static short prev_state = 0;

  short current_state = 0;
  for(short i = 0; i < len; i++) {
    if (digitalRead(pins[i]) == LOW) {
//      Serial.println(pins[i], DEC);
      current_state |= (1 << i);
    }
  }

  short ret = 0;

  if(current_state != prev_state) {
//    Serial.println(current_state, BIN);
    // state change
    if(current_state == 0) {
      // no buttons pressed
      if(millis() - button_timer > min_press_time) {
        ret = prev_state;
      }
    } else {
      // new button pressed
      if (current_state != 0) {
        button_timer = millis();
      }
    }
  }

  prev_state = current_state;
  return ret;
}
