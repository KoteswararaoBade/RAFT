import os
import time

from state.state import State
from util.loggingutil import LoggingUtil

logger = LoggingUtil(os.path.basename(__file__)).get_logger()


class Leader(State):

    def __init__(self, server_ip_address, peers):
        super().__init__(server_ip_address, peers)
        # volatile state on leaders
        self._next_index = {(peer.ip_address, peer.port): len(self.log) + 1 for peer in self.peers}
        self._match_index = {(peer.ip_address, peer.port): 0 for peer in self.peers}


    @property
    def next_index(self):
        return self._next_index

    @next_index.setter
    def next_index(self, next_index):
        self._next_index = next_index

    @property
    def match_index(self):
        return self._match_index

    @match_index.setter
    def match_index(self, match_index):
        self._match_index = match_index


    def send_heart_beats(self):
        while True:
            for peer in self.peers:
                try:
                    logger.info('Sending heart beat to peer {}'.format(peer))
                    peer.send_heart_beat(self.server_id, self.current_term)
                except Exception as e:
                    logger.error('Error sending heart beat to peer {}'.format(peer))
            time.sleep(1)