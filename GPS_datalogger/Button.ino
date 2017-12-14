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
