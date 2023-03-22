import os

from message.request_vote_message import RequestVoteMessage
from .state import State
from util.loggingutil import LoggingUtil

logger = LoggingUtil(os.path.basename(__file__)).get_logger()

class Candidate(State):

    def __init__(self, server_ip_address, peers):
        super().__init__(server_ip_address, peers)


    def build_request_vote_message(self):
        last_log_index = len(self.log) - 1
        last_log_term = self.log[last_log_index].term_number
        return RequestVoteMessage(self.current_term, self.server_id, last_log_index, last_log_term)

    def start_election(self):
        # set current term
        self._current_term += 1
        logger.info("Starting election for term {}".format(self.current_term))
        # vote for self
        self._voted_for[self.current_term] = self.server_id
        self._total_votes = 1
        # reset election timeout
        # send request vote RPCs to all other servers
        for peer in self.peers:
            try:
                response = peer.send_request_vote(self.build_request_vote_message())
                logger.info("Received response from peer {}: {}".format(peer, response))
                if response:
                    peer_vote, peer_term_number = response
                    if peer_term_number > self.current_term:
                        # demote to follower
                        return State.FOLLOWER, peer_term_number
                    elif peer_term_number == self.current_term:
                        if peer_vote:
                            self._total_votes += 1
                            if 2*self._total_votes > len(self.peers) + 1:
                                # become leader
                                return State.LEADER, self.current_term
            except Exception as e:
                logger.error("Error while sending request vote to peer {}: {}".format(peer, e))
                continue
        return State.CANDIDATE, self.current_term




