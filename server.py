from pymidi import server
import logging
import threading


def execute_thread(func, *args):
  thread = threading.Thread(target=func, args=args)
  thread.start()
  return thread



class MIDIHandler(server.Handler):
    def __init__(self, hand):
      self.logger = logging.getLogger(__name__)
      self.hand = hand
      # self.rail = rail
      # self.key_positions = {
      #   36: 0,
      #   35: 0
      # }
      # key_dist = 1525/23
      # for i in range(34, 11, -1):
      #   self.key_positions[i] = round(self.key_positions[i+1] + key_dist)
      # print(self.key_positions[12])
    


    def on_peer_connected(self, peer):
        self.logger.info('Peer connected: {}'.format(peer))

    def on_peer_disconnected(self, peer):
        self.logger.info('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        for command in command_list:
          self.logger.info(' '.join('Recieved command {} {} on ch{}  from {}'
          .format(command.command,command.params, 
          command.channel, peer.name).split()))
          if command.command == 'note_on':
            self.hand.handle_note_command(command)
          elif command.command == 'control_mode_change':
            self.hand.handle_control_change(command)
            # if command.command == 'note_on':
            #     key = command.params.key
            #     velocity = command.params.velocity
            #     print('Someone hit the key {} with velocity {}'.format(key, velocity))


if __name__=="__main__":
  import time
  import sys
  sys.path.append('drivers')
  from drivers.linear_actuator import LinearActuator
  from drivers.serial_control import SerialController
  from drivers.servo import HandServos
  from hand import Hand

  logging.basicConfig(level=logging.INFO, format='[%(asctime)s.%(msecs)03d][%(levelname)s]:\t%(message)s', datefmt='%m/%d/%Y %H:%M:%S')
  sc = SerialController('/dev/ttyACM0')
  rail = LinearActuator(sc)
  index = HandServos.format_servo_data('index', 0, max_angle=35, inverted=True)
  middle = HandServos.format_servo_data('middle', 1, max_angle=35, inverted=True)
  ring = HandServos.format_servo_data('ring', 2, max_angle=62)
  pinkie = HandServos.format_servo_data('pinkie', 3, min_angle=10, max_angle=70)
  
  hs = HandServos([index, middle, ring, pinkie])
  hand = Hand(rail, hs)
  port = 5051
  midi_server = server.Server([('::', port)])
  midi_server.add_handler(MIDIHandler(hand))
  # t = threading.Thread(target=loop_runner, daemon=True)
  # t.start()
  midi_server.serve_forever()
  