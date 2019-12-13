const int dir_pin = 3;
const int step_pin = 2;
const int near_pin = 4;
const int far_pin = 5;
int invert_direction = 0;
int switch_delay = 400;
int step_delay = 800;
int position = 0;
int direction = 0;
int target_position = 0;
int running = 0;
int near_switch = 1;
int far_switch = 1;
int step_length = 1680;
int step_id = 0;
int slowdown_start = 75;
int slowdown_factor = 50;
int prev_pos = 0;

int get_slowdown_delay(){
  int remaining_steps = abs(position - target_position);
  if (remaining_steps > slowdown_start)
    return 0;
  int slowdown_delay = slowdown_factor * (slowdown_start - remaining_steps/2);
  return slowdown_delay;
}

int get_speedup_delay() {
  int steps = abs(prev_pos - position);
  if (steps > slowdown_start)
    return 0;
  return slowdown_factor * (steps/2);
}

void send_serial_msg(int id, int status, int data) {
  byte buf[4];
  buf[0] = id & 255;
  buf[1] = status & 255;
  buf[2] = (data >> 8)  & 255;
  buf[3] = data & 255;

  Serial.write(buf, 4);
}

void set_direction(int d) {
  d = d? 1 : 0;
  if(invert_direction)
    d = !d;
  direction = d;
  digitalWrite(dir_pin, direction);
}

void zero_motor() {
  running = 1;
  set_direction(1);
  near_switch = digitalRead(near_pin);
  while (near_switch) {
    digitalWrite(step_pin, HIGH);
    delayMicroseconds(switch_delay);
    digitalWrite(step_pin, LOW);
    delayMicroseconds(step_delay);
    near_switch = digitalRead(near_pin);
  }
  running = 0;
  position = 0;
}

void calibrate() {
  zero_motor();
  position = 0;
  step_length = 0;
  set_direction(0);
  while(far_switch) {
    digitalWrite(step_pin, HIGH);
    delayMicroseconds(switch_delay);
    digitalWrite(step_pin, LOW);
    delayMicroseconds(step_delay);
    far_switch = digitalRead(far_pin);
    step_length++;
  }
  set_direction(1);
  for (int i = 0; i < step_length; i++){
    step();
    delayMicroseconds(step_delay); 
  }
}

void step() {
  digitalWrite(step_pin, HIGH);
  delayMicroseconds(switch_delay);
  digitalWrite(step_pin, LOW);
  int dir = direction? -1: 1;
  position += dir;
}

void setup() {
  // put your setup code here, to run once:
  pinMode(dir_pin,OUTPUT);
  pinMode(step_pin,OUTPUT);
  pinMode(near_pin, INPUT_PULLUP);
  pinMode(far_pin, INPUT_PULLUP);
  digitalWrite(dir_pin, direction);
  Serial.begin(9600);
  zero_motor();
}

void loop() {
  if(running) 
    if(position == target_position /*|| (!far_switch && !direction || !near_switch && direction)*/) {
      running = 0;
      // respond to pi to indicate stepping has finished;
      send_serial_msg(step_id, 1, position);
    }
    else {
      step();
    }
  int begin_time = micros();
  near_switch = digitalRead(near_pin);
  far_switch = digitalRead(far_pin);

  if (Serial.available() >= 4) {
    // read the incoming byte:
    int msg_id = Serial.read();
    int status_code = Serial.read();
    int value = Serial.read();
    value <<= 8;
    value += Serial.read();


    switch(status_code) {
    case 0:
      calibrate();
      send_serial_msg(msg_id,0, step_length);
      break;
    case 1: // Requst Step
      if(running){ //send a step error if stepper is already running
        send_serial_msg(msg_id, 10, 0);
        break;
      }
      step_id = msg_id;
      target_position = value;
      if(target_position > step_length)
        target_position = step_length;
      else if(target_position < 0)
        target_position = 0;
      // Set direction based on target position
      if (target_position < position)
        set_direction(1);
      else{
        set_direction(0);
        if(target_position - position > 5)
          target_position -= 5);
      }
      running = 1;
      prev_pos = position;
      break;
    case 2: // Set position
      if(running)
        send_serial_msg(msg_id, 10, 0);
      else {
        position = value;
        send_serial_msg(msg_id, 2, 1);
      }
      break;
    case 3: // Get Position
      send_serial_msg(msg_id, 3, position);
      break;
    case 4: // Set switch delay
      switch_delay = value;
      send_serial_msg(msg_id, 4, 1);
      break;
    case 5: // Get switch delay
      send_serial_msg(msg_id, 5, switch_delay);
      break;
    case 6: // Set step delay
      step_delay = value;
      send_serial_msg(msg_id, 6, 1);
      break;
    case 7: // Get step delay
      send_serial_msg(msg_id, 7, step_delay);
      break;
    case 8: // Force Stop
      if(!running)
        send_serial_msg(msg_id, 8, 0);
      else {
        target_position = position;
        send_serial_msg(msg_id, 8, 1);
      }
      break;
    case 9: // Get Limit switch values
      // process this when limit switches are on installed..
      if(value)
        send_serial_msg(msg_id, 9, far_switch);
      else
        send_serial_msg(msg_id, 9, near_switch);
      break;
    case 12: // Zero Stepper Motor
      zero_motor();
      send_serial_msg(msg_id, 12, 1);
      break;
    default:
      send_serial_msg(msg_id, 11, -1);
    }
  }
  
  int sld = get_slowdown_delay();
  int spd = get_speedup_delay();
  int tld = sld > spd? sld : spd;

  // get time it took to process serial messages;
  int serial_time = micros() - begin_time;
  int step_diff = step_delay + tld - serial_time;
  if(step_diff < 0)
    step_diff = 0;

  delayMicroseconds(step_diff);
}
