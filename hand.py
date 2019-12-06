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

def execute_thread(func, *args):
  thread = threading.Thread(target=func, args=args)
  thread.start()
  return thread

# 73 72 5 84
finger_controller_mappings = {
  73: 'index', 72: 'middle', 5: 'ring', 84: 'pinkie'
}
class Hand:

    def __init__(self, rail, servos):
        self.rail = rail
        self.servos = servos
        self.queue_lock = threading.Lock()
        self.note_queue = []
        self.key_positions = {(WHITE_KEYS + BLACK_KEYS -1): 0}
        self.last_requested_key = 0
        self.last_requested_offset = 0
        self.controller_vals = {}
        for key in finger_controller_mappings.keys():
          self.controller_vals[key] = 0

        for i in range((WHITE_KEYS + BLACK_KEYS -2), -1, -1):
            if i+1 in BLACK_KEY_POSITIONS:
                self.key_positions[i] = self.key_positions[i+2] + int((KEY_WIDTH + GAP_WIDTH) * STEPS_PER_CM)
            elif i in BLACK_KEY_POSITIONS:
                self.key_positions[i] = self.key_positions[i+1] + int((KEY_WIDTH/2) * STEPS_PER_CM)
            else:
                self.key_positions[i] = self.key_positions[i+1] + int((KEY_WIDTH + GAP_WIDTH) * STEPS_PER_CM)        


    def handle_note_command(self, command):
        number = command.params.key.intvalue 
        if command.command == 'note_on':
            key = command.params.key.intvalue
            octave_offset = int((key+1)/TOTAL_KEYS)
            if (key % 24 == 0):
              previous_offset = self.last_requested_offset
              if previous_offset - octave_offset == 1 or (not previous_offset and octave_offset == 1):
                octave_offset = previous_offset
            offset_pos = octave_offset * 24
            key_pos = key - offset_pos

            if key_pos in self.key_positions:
              if self.rail.is_running():
                self.rail.force_stop()
              execute_thread(self.rail.step, self.key_positions[key_pos])
              self.last_requested_key = key
              self.last_requested_offset = octave_offset
            else:
                print(str(key) + " " + str(key_pos))

    def handle_control_change(self, command):
      if command.params.controller in finger_controller_mappings:
        controller = command.params.controller
        val = command.params.value
        if val > self.controller_vals[controller]:
          self.servos.full_angle(finger_controller_mappings[controller], 1)
        elif val < self.controller_vals[controller]:
          self.servos.full_angle(finger_controller_mappings[controller], 0)
        self.controller_vals[controller] = val