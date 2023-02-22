import os
import time

from state.state import State
from util.loggingutil import LoggingUtil

logger = LoggingUtil(os.path.basename(__file__)).get_logger()


class Leader(State):

    def __init__(self, server_ip_address, log, peers):
        super().__init__(server_ip_address, log, peers)


    def send_heart_beats(self):
        while True:
            for peer in self.peers:
                try:
                    logger.info('Sending heart beat to peer {}'.format(peer))
                    peer.send_heart_beat(self.server_id, self.current_term)
                except Exception as e:
                    logger.error('Error sending heart beat to peer {}'.format(peer))
            time.sleep(1)