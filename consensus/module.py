import os
import random
import threading
import time

from network.server import Server
from state.follower import Follower
from state.candidate import Candidate
from state.leader import Leader
from state.state import State

from util.rpcutil import RPCServer
from util.loggingutil import LoggingUtil

logger = LoggingUtil(os.path.basename(__file__)).get_logger()


def get_random_election_timeout(start, end):
    return random.randint(start, end) / 1000


class ConsensusModule(RPCServer):

    def __init__(self, host, port, peers):
        super().__init__(host, port)
        self._id = (host, port)
        self.state = Follower((host, port), [], peers)

    def start(self):
        host, port = self._id
        logger.info("Starting network at %s:%s" % (host, port))
        server_thread = threading.Thread(target=super(ConsensusModule, self).start)
        # server_thread.daemon = True
        server_thread.start()
        logger.info("Server loop running in thread: %s" % server_thread.name)
        self.start_timer()

    def stop(self):
        self.server.stop()


    def get_new_state(self, state_type):
        state = None
        if state_type == State.FOLLOWER:
            state = Follower(None, [], [])
        elif state_type == State.CANDIDATE:
            state = Candidate(None, [], [])
        elif state_type == State.LEADER:
            state = Leader(None, [], [])
        state.set_all_properties(self.state)
        return state


    def request_vote(self, candidate_id, term_number):
        logger.info('Received vote request from {} with term number {}'.format(candidate_id, term_number))
        if term_number < self.state.current_term or term_number in self.state.voted_for:
            logger.info('Rejecting vote request from {} with term number {}'.format(candidate_id, term_number))
            return False, self.state.current_term
        logger.info('Voting for candidate {} with term number {}'.format(candidate_id, term_number))
        self.state.voted_for[term_number] = candidate_id
        self.state.current_term = term_number
        return True, self.state.current_term

    def start_election(self):
        # upgrade state to candidate if not already candidate
        if isinstance(self.state, Follower):
            logger.info("Upgrading state to candidate")
            self.state = self.get_new_state(State.CANDIDATE)
        # send request vote to all peers
        next_state_type, term = self.state.start_election()
        if next_state_type == State.FOLLOWER:
            logger.info("Downgrading state to follower")
            self.state = self.get_new_state(State.FOLLOWER)
        # if majority votes for you, become leader
        elif next_state_type == State.LEADER:
            logger.info("Upgrading state to leader")
            self.state = self.get_new_state(State.LEADER)


    def start_timer(self):
        election_time_out = get_random_election_timeout(5000, 8000)
        sleep_time = 0.2
        logger.info("=====================================")
        logger.info("Starting timer with election timeout of {} seconds".format(election_time_out))
        latest_timestamp = time.time()
        while (time.time() - latest_timestamp) < election_time_out or (not isinstance(self.state, Leader)):
            time.sleep(sleep_time)
        logger.info("Election timeout reached")
        if isinstance(self.state, Leader):
            logger.info("Not starting election since I am already leader")
            return
        # start election on new thread
        t = threading.Thread(target=self.start_election)
        t.start()
        self.start_timer()


if __name__ == '__main__':
    consensus = ConsensusModule('10.181.93.155', 8080, [('10.181.91.9', 8080)])
    consensus.start()
