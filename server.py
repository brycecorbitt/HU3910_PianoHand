from pymidi import server
import logging

class MIDIHandler(server.Handler):
    def __init__(self):
      self.logger = logging.getLogger(__name__)

    def on_peer_connected(self, peer):
        self.logger.info('Peer connected: {}'.format(peer))

    def on_peer_disconnected(self, peer):
        self.logger.info('Peer disconnected: {}'.format(peer))

    def on_midi_commands(self, peer, command_list):
        for command in command_list:
          self.logger.info(' '.join('Recieved command {} {} on ch{}  from {}'
          .format(command.command,command.params, 
          command.channel, peer.name).split()))
            # if command.command == 'note_on':
            #     key = command.params.key
            #     velocity = command.params.velocity
            #     print('Someone hit the key {} with velocity {}'.format(key, velocity))

# if __name__=="__main__":
#   logging.basicConfig(level=logging.INFO, format='[%(asctime)s.%(msecs)03d][%(levelname)s]:\t%(message)s', datefmt='%m/%d/%Y %H:%M:%S')
#   port = 5051
#   midi_server = server.Server([('::', port)])
#   midi_server.add_handler(MIDIHandler())
#   midi_server.serve_forever()
  