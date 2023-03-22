import os
import random
import threading
import time
import json

from message.request_vote_message import RequestVoteMessage
from state.state import State

from util.rpcutil import RPCServer
from util.loggingutil import LoggingUtil

logger = LoggingUtil(os.path.basename(__file__)).get_logger()


def get_random_election_timeout(start, end):
    return random.randint(start, end) / 1000


class ConsensusModule(RPCServer):

    def __init__(self, host, port, peers, election_timeout_range, heartbeat_interval, sleep_time):
        super().__init__(host, port)
        self._id = (host, port)
        self.state = State((host, port), peers, State.FOLLOWER)
        self.latest_timestamp = time.time()
        self.election_timeout_start = election_timeout_range[0]
        self.election_timeout_end = election_timeout_range[1]
        self.heartbeat_interval = heartbeat_interval/1000
        self.sleep_time = sleep_time/1000

    def start(self):
        host, port = self._id
        logger.info("Starting network at %s:%s" % (host, port))
        server_thread = threading.Thread(target=super(ConsensusModule, self).start)
        # server_thread.daemon = True
        server_thread.start()
        logger.info("Server loop running in thread: %s" % server_thread.name)
        self.start_timer()
        self.state.state_type = State.LEADER
        # self.state = self.get_new_state(State.LEADER)
        self.send_heart_beats(self.heartbeat_interval)

    def stop(self):
        self.server.stop()


    # TODO: implement this
    # def get_new_state(self, state_type):
    #     state = None
    #     if state_type == State.FOLLOWER:
    #         state = Follower(None, [])
    #     elif state_type == State.CANDIDATE:
    #         state = Candidate(None, [])
    #     elif state_type == State.LEADER:
    #         state = Leader(None, [])
    #     state.set_all_properties(self.state)
    #     return state

    def reset_timer(self):
        self.latest_timestamp = time.time()

    # REQUEST VOTE RPC RECEIVER
    def request_vote(self, message):
        # sender details
        sender_candidate_id = message['_candidate_id']
        sender_last_log_index = message['_last_log_index']
        sender_last_log_term = message['_last_log_term']
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
        if self.state.state_type != State.FOLLOWER:
            logger.info("Downgrading state to follower")
            self.state.state_type = State.FOLLOWER
            # self.state = self.get_new_state(State.FOLLOWER)
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

    # HEART BEAT RPC RECEIVER
    def heart_beat(self, leader_id, term_number):
        logger.info('Received heart beat from leader {} with term number {}'.format(leader_id, term_number))
        if term_number < self.state.current_term:
            logger.info('Rejecting heart beat from {} as current term number is {}'.format(leader_id, self.state.current_term))
        else:
            self.reset_timer()
            logger.info('Acknowledging heart beat from {} with term number {}'.format(leader_id, term_number))
            self.state.current_term = term_number
            self.state.leader_id = leader_id
            self.state.state_type = State.FOLLOWER
            # self.state = self.get_new_state(State.FOLLOWER)
        return True, self.state.current_term

    # SEND HEART BEAT RPC
    def send_heart_beats(self, heart_beat_interval):
        while True:
            if self.state.state_type != State.LEADER:
                break
            for peer in self.state.peers:
                try:
                    logger.info('Sending heart beat to peer {}'.format(peer))
                    peer.send_heart_beat(self.state.server_id, self.state.current_term)
                except Exception as e:
                    logger.error('Error sending heart beat to peer {}'.format(peer))
            time.sleep(heart_beat_interval)

    # SEND REQUEST VOTE RPC
    def send_request_vote(self, peer):
        try:
            response = peer.send_request_vote(self.build_request_vote_message())
            logger.info("Received response from peer {}: {}".format(peer, response))
            if response:
                peer_vote, peer_term_number = response
                if peer_term_number > self.state.current_term:
                    # demote to follower
                    return State.FOLLOWER, peer_term_number
                elif peer_term_number == self.state.current_term:
                    if peer_vote:
                        self.state.total_votes += 1
                        if 2 * self.state.total_votes > len(self.state.peers) + 1:
                            # become leader
                            return State.LEADER, self.state.current_term
        except Exception as e:
            logger.error("Error while sending request vote to peer {}: {}".format(peer, e))
        return State.CANDIDATE, self.state.current_term

    def start_election(self):
        # upgrade state to candidate if not already candidate
        if self.state.state_type == State.FOLLOWER:
            logger.info("Upgrading state to candidate")
            self.state.state_type = State.CANDIDATE
            # self.state = self.get_new_state(State.CANDIDATE)
        # send request vote to all peers
        self.state.current_term += 1
        logger.info("Starting election for term {}".format(self.state.current_term))
        # vote for self
        self.state.voted_for[self.state.current_term] = self.state.server_id
        self.state.total_votes = 1
        for peer in self.state.peers:
            next_state_type, term = self.send_request_vote(peer)
            if next_state_type == State.FOLLOWER:
                logger.info("Downgrading state to follower")
                self.state.state_type = State.FOLLOWER
                # self.state = self.get_new_state(State.FOLLOWER)
                break
            # if majority votes for you, become leader
            elif next_state_type == State.LEADER:
                logger.info("Upgrading state to leader")
                self.state.state_type = State.LEADER
                # self.state = self.get_new_state(State.LEADER)
                break

    # build request vote message
    def build_request_vote_message(self):
        last_log_index = len(self.state.log) - 1
        last_log_term = self.state.log[last_log_index].term_number
        return RequestVoteMessage(self.state.current_term, self.state.server_id, last_log_index, last_log_term)

    def start_timer(self):
        election_time_out = get_random_election_timeout(self.election_timeout_start, self.election_timeout_end)
        logger.info("=====================================")
        logger.info("Starting timer with election timeout of {} seconds".format(election_time_out))
        self.reset_timer()
        while (time.time() - self.latest_timestamp) < election_time_out and (self.state.state_type != State.LEADER):
            time.sleep(self.sleep_time)
        if self.state.state_type == State.LEADER:
            logger.info("I am leader so election timeout not required")
            return
        logger.info("Election timeout reached")
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
    election_timeout_range = config_json['election_timeout_range']
    heartbeat_interval = config_json['heartbeat_interval']
    sleep_time = config_json['sleep_time']
    consensus = ConsensusModule(config_json['host'], config_json['port'], peers, election_timeout_range, heartbeat_interval, sleep_time)
    consensus.start()
    # run below in a separate thread
    # uvicorn.run(app, host="localhost", port=8000)
    # threading.Thread(target=uvicorn.run, args=(app,), kwargs={'host': 'localhost', 'port': 8000}).start()


if __name__ == '__main__':
    run()
