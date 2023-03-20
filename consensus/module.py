import os
import random
import threading
import time
import json

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
        self.state = Follower((host, port), peers)
        self.latest_timestamp = time.time()

    def start(self):
        host, port = self._id
        logger.info("Starting network at %s:%s" % (host, port))
        server_thread = threading.Thread(target=super(ConsensusModule, self).start)
        # server_thread.daemon = True
        server_thread.start()
        logger.info("Server loop running in thread: %s" % server_thread.name)
        self.start_timer()
        self.state = self.get_new_state(State.LEADER)
        self.state.send_heart_beats()

    def stop(self):
        self.server.stop()

    def get_new_state(self, state_type):
        state = None
        if state_type == State.FOLLOWER:
            state = Follower(None, [])
        elif state_type == State.CANDIDATE:
            state = Candidate(None, [])
        elif state_type == State.LEADER:
            state = Leader(None, [])
        state.set_all_properties(self.state)
        return state

    def reset_timer(self):
        self.latest_timestamp = time.time()

    def request_vote(self, message):
        # sender details
        print(message['_content'], "message")
        sender_candidate_id = message['_content']['candidate_id']
        sender_last_log_index = message['_content']['last_log_index']
        sender_last_log_term = message['_content']['last_log_term']
        sender_term_number = message['_term_number']
        # peer details
        peer_last_log_index = len(self.state.log) - 1
        peer_last_log_term = self.state.log[peer_last_log_index].term_number
        logger.info('Received vote request from {} with term number {}'.format(sender_candidate_id, sender_term_number))

        # if same requester has asked for vote in the same term and peer has already voted for
        # that candidate, then return true
        if sender_term_number == self.state.current_term and sender_term_number in self.state.voted_for and \
                self.state.voted_for[sender_term_number] == sender_candidate_id:
            return True, self.state.current_term

        # if sender's term number is less than peer's current term number, then reject the vote request
        if sender_term_number < self.state.current_term:
            logger.info('Rejecting vote request from {} due to lesser term number {}'.format(sender_candidate_id, sender_term_number))
            return False, self.state.current_term

        # if peer has already voted for some other candidate in the same term, then reject the vote request
        if sender_term_number in self.state.voted_for and self.state.voted_for[sender_term_number] != sender_candidate_id:
            logger.info('Rejecting vote request from {} due to already voted for {}'.format(sender_candidate_id, self.state.voted_for[sender_term_number]))
            return False, self.state.current_term

        # if peer's term number is less than sender's term number, then downgrade peer's state to follower
        if not isinstance(self.state, Follower):
            logger.info("Downgrading state to follower")
            self.state = self.get_new_state(State.FOLLOWER)
            # reset election timeout
            self.reset_timer()

        # if sender's log is not up-to-date, then reject the vote request
        if (peer_last_log_term > sender_last_log_term) or \
                (peer_last_log_term == sender_last_log_term and peer_last_log_index > sender_last_log_index):
            logger.info('Rejecting vote request from {} due to stale log'.format(sender_candidate_id))
            return False, self.state.current_term

        # all conditions are satisfied, so vote for the candidate
        logger.info('Voting for candidate {} with term number {}'.format(sender_candidate_id, sender_term_number))
        self.state.current_term = sender_term_number
        self.state.voted_for[self.state.current_term] = sender_candidate_id
        return True, self.state.current_term

    def heart_beat(self, leader_id, term_number):
        logger.info('Received heart beat from leader {} with term number {}'.format(leader_id, term_number))
        if term_number < self.state.current_term:
            logger.info('Rejecting heart beat from {} with term number {}'.format(leader_id, term_number))
        else:
            self.reset_timer()
            logger.info('Acknowledging heart beat from {} with term number {}'.format(leader_id, term_number))
            self.state.current_term = term_number
            self.state.leader_id = leader_id
            self.state = self.get_new_state(State.FOLLOWER)
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
        self.reset_timer()
        while (time.time() - self.latest_timestamp) < election_time_out and (not isinstance(self.state, Leader)):
            time.sleep(sleep_time)
        logger.info("Election timeout reached")
        if isinstance(self.state, Leader):
            logger.info("Not starting election since I am already leader")
            return
        # start election on new thread
        t = threading.Thread(target=self.start_election)
        t.start()
        self.start_timer()


def process_json_config(filename):
    with open(filename) as f:
        config = json.load(f)
    return config


def run():
    config_json = process_json_config('../config.json')
    peers = [(peer['host'], peer['port']) for peer in config_json['peers']]
    consensus = ConsensusModule(config_json['host'], config_json['port'], peers)
    consensus.start()


if __name__ == '__main__':
    run()
