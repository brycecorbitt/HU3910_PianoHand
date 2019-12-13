import time
import threading

WHITE_KEYS = 15
BLACK_KEYS = 10
TOTAL_KEYS = WHITE_KEYS + BLACK_KEYS
KEY_WIDTH = 2
GAP_WIDTH = .06
MOVEMENT_WIDTH = WHITE_KEYS * KEY_WIDTH + (WHITE_KEYS -1) * GAP_WIDTH
STEP_WIDTH = 1625
STEPS_PER_CM = STEP_WIDTH/MOVEMENT_WIDTH
BLACK_KEY_POSITIONS = [1, 3, 6, 8, 10, 13, 15, 18, 20, 22]
WHITE_KEY_POSITIONS = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24]
STEP_RECORDINGS = [1290, 1175, 1055, 935, 825, 705, 585, 470, 353, 234, 113, 0]
FINGER_LABELS = ['index', 'middle', 'ring', 'pinky']
pos_mappings = {}
for i in range(len(WHITE_KEY_POSITIONS)):
  current = WHITE_KEY_POSITIONS[i]
  pos_mappings[current] = {}
  for j in range(len(FINGER_LABELS)-1,-1,-1):
    net_pos = i-j
    if net_pos < 0 or net_pos > len(STEP_RECORDINGS) -1:
      continue
    pos_mappings[current][net_pos] = FINGER_LABELS[j]
print(pos_mappings)
# print(pos_mappings)


def execute_thread(func, *args):
  thread = threading.Thread(target=func, args=args)
  thread.start()
  return thread

# 73 72 5 84
finger_controller_mappings = {
  73: 'index', 72: 'middle', 5: 'ring', 84: 'pinky'
}
class Hand:
    def __init__(self, rail, servos):
        self.rail = rail
        self.servos = servos
        self.queue_lock = threading.Lock()
        self.note_queue = []
        # self.key_positions = {(WHITE_KEYS + BLACK_KEYS -1): 0}
        self.position_index = 11
        self.last_requested_key = 0
        self.last_requested_offset = 0
        self.controller_vals = {}
        for key in finger_controller_mappings.keys():
          self.controller_vals[key] = 0
        self.fingers_active = {}
        for finger in FINGER_LABELS:
          self.fingers_active[finger] = False
        

        # for i in range((WHITE_KEYS + BLACK_KEYS -2), -1, -1):
        #     if i+1 in BLACK_KEY_POSITIONS:
        #         self.key_positions[i] = self.key_positions[i+2] + int((KEY_WIDTH + GAP_WIDTH) * STEPS_PER_CM)
        #     elif i in BLACK_KEY_POSITIONS:
        #         self.key_positions[i] = self.key_positions[i+1] + int((KEY_WIDTH/2) * STEPS_PER_CM)
        #     else:
        #         self.key_positions[i] = self.key_positions[i+1] + int((KEY_WIDTH + GAP_WIDTH) * STEPS_PER_CM) 
    def rail_ready(self):
      print(self.fingers_active.values())
      if any(val == True for val in self.fingers_active.values()):
        return False
      return True       

    def hit_key(self, pos, finger):
      step_position = STEP_RECORDINGS[pos]
      if pos != self.position_index:
        while not self.rail_ready():
          time.sleep(.05)
        self.rail.step(step_position)
        self.position_index = pos
      self.fingers_active[finger] = True
      self.servos.full_angle(finger, 1)
      # time.sleep(1)
      # self.servos.full_angle(finger, 0)
    
    def release_key(self, finger):
      self.servos.full_angle(finger, 0)
      time.sleep(.5)
      self.fingers_active[finger] = False
      

    def handle_note_command(self, command):
        key = command.params.key.intvalue
        if command.command == 'note_on':
            if key == 127:
              for finger in FINGER_LABELS:
                self.servos.full_angle(finger, 0)
                time.sleep(.5)
                self.fingers_active[finger] = False
              execute_thread(self.rail.zero_motor()).join()
              return
            # Get Position of key on keyboard
            octave_offset = int((key+1)/TOTAL_KEYS)
            if (key % 24 == 0):
              previous_offset = self.last_requested_offset
              if previous_offset - octave_offset == 1 or (not previous_offset and octave_offset == 1):
                octave_offset = previous_offset
            offset_pos = octave_offset * 24
            key_pos = key - offset_pos
            print(key_pos)
            if key_pos == 0:
              execute_thread(self.hit_key, 0, 'index')
              return

            if key_pos in BLACK_KEY_POSITIONS:
              key_index = BLACK_KEY_POSITIONS.index(key_pos)
              while not self.rail_ready():
                time.sleep(.05)
              self.rail.step(STEP_RECORDINGS[key_index])
              self.position_index = key_index
              return
            if key_pos in pos_mappings:
              if self.rail.is_running():
                self.rail.force_stop()

              key_list = list(pos_mappings[key_pos].keys())
              key_index = None

              min = 100
              closest_pos = 100
              for key in key_list:
                if abs(self.position_index - key) < min:
                  min = abs(self.position_index - key)
                  closest_pos = key
              if closest_pos > len(STEP_RECORDINGS):
                return
              key_index = closest_pos
              print(key_index)
              # print(key_index
              # )
              
              # for key in key_list:
              #   if pos_mappings[key_pos] == self.position_index:
              #     key_index = self.position_index
              
              if key_index is None:
                return
              # execute_thread(self.hit_key(step_position))
              execute_thread(self.hit_key, key_index, pos_mappings[key_pos][key_index])
              self.last_requested_key = key
              self.last_requested_offset = octave_offset
            else:
                print(str(key) + " " + str(key_pos))
        elif command.command == 'note_off':
          octave_offset = int((key+1)/TOTAL_KEYS)
          if (key % 24 == 0):
            previous_offset = self.last_requested_offset
            if previous_offset - octave_offset == 1 or (not previous_offset and octave_offset == 1):
              octave_offset = previous_offset
          offset_pos = octave_offset * 24
          key_pos = key - offset_pos
          if key_pos in pos_mappings and self.position_index in pos_mappings[key_pos]:
            execute_thread(self.release_key, pos_mappings[key_pos][self.position_index])



    def handle_control_change(self, command):
      if command.params.controller in finger_controller_mappings:
        controller = command.params.controller
        val = command.params.value
        if val > self.controller_vals[controller]:
          self.servos.full_angle(finger_controller_mappings[controller], 1)
        elif val < self.controller_vals[controller]:
          self.servos.full_angle(finger_controller_mappings[controller], 0)
        self.controller_vals[controller] = val

""" STEP RECORDINGS
0
99
205
315
430
548
668
774
889
1003
1116
1235
"""
if __name__=="__main__":
  import time
  import sys
  sys.path.append('drivers')
  from drivers.linear_actuator import LinearActuator
  from drivers.serial_control import SerialController
  from drivers.servo import HandServos
  from hand import Hand
  from attrdict import AttrDict

  sc = SerialController('/dev/ttyACM0')
  rail = LinearActuator(sc)
  index = HandServos.format_servo_data('index', 0, min_angle=20, max_angle=80, inverted=True)
  middle = HandServos.format_servo_data('middle', 1, min_angle=44, max_angle=100, inverted=True)
  ring = HandServos.format_servo_data('ring', 2, min_angle=10, max_angle=75)
  pinky = HandServos.format_servo_data('pinky', 3, max_angle=65)
  
  hs = HandServos([index, middle, ring, pinky])
  hand = Hand(rail, hs)
  time.sleep(4)
  def create_packet(command, note):
    params = AttrDict({'command': command, 'params': {'key': {'intvalue': note}}})
    return params
  def on(num):
    hand.handle_note_command(create_packet('note_on', num))
  def off(num):
    hand.handle_note_command(create_packet('note_off', num))
  on(0)
  time.sleep(4)
  on(2)
  off(0)
  time.sleep(2)
  off(2)
  time.sleep(2)
  # on(16)
  # time.sleep(2)
  # on(2)
  # on(17)
  # time.sleep(2)
  # off(16)
  # off(17)
  # time.sleep(4)
  # off(2)
  # for _ in range(3):
  #   start = time.time()
  #   print(hand.rail.calibrate())
  #   print(time.time() - start)

  # Rail Check
  # while True:
  #   input_number = int(input())
  #   if input_number >= len(STEP_RECORDINGS):
  #     continue
  #   if input_number >=0:
  #     hand.rail.step(STEP_RECORDINGS[input_number])
  #   else:
  #     hand.rail.zero_motor()




  