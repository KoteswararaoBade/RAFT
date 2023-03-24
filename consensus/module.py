import os
import random
import threading
import time
import json

from log.log import LogEntry
from message.append_entries_message import AppendEntriesMessage
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
        self.change_state_properties()
        # self.state = self.get_new_state(State.LEADER)
        self.send_heart_beats(self.heartbeat_interval)

    def stop(self):
        self.server.stop()

    def change_state_properties(self):
        if self.state.state_type == State.FOLLOWER:
            self.state.total_votes = 0
        elif self.state.state_type == State.LEADER:
            self.state.next_index = {(peer.host, peer.port): len(self.state.log) + 1 for peer in self.state.peers}
            self.state.match_index = {(peer.host, peer.port): 0 for peer in self.state.peers}

    def reset_timer(self):
        self.latest_timestamp = time.time()

    # ==================================================================================
    # RPC RECEIVERS
    # ==================================================================================

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
            self.change_state_properties()
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
            self.change_state_properties()
        return True, self.state.current_term

    def append_entries(self, message):
        print('Received append entries request message {}'.format(message))
        leader_term_number = message['_term_number']
        leader_id = message['_leader_id']
        leader_prev_log_index = message['_prev_log_index']
        leader_prev_log_term = message['_prev_log_term']
        if leader_term_number < self.state.current_term:
            return False, self.state.current_term, None
        if len(self.state.log) <= leader_prev_log_index:
            print('Rejecting append entries request as peer log is shorter than leader log')
            print('Peer log: {}'.format(self.state.log))
            return False, self.state.current_term, len(self.state.log)
        if self.state.log[leader_prev_log_index].term_number != leader_prev_log_term:
            print('Rejecting append entries request as peer log is not in sync with leader log')
            print('Peer log: {}'.format(self.state.log))
            mismatched_term_number = self.state.log[leader_prev_log_index].term_number
            index = leader_prev_log_index
            while self.state.log[index].term_number == mismatched_term_number:
                index -= 1
            return False, self.state.current_term, index + 1
        # positive case
        # if there are some entries in the log which are above the leader's prev log index, then delete them
        if len(self.state.log) > leader_prev_log_index + 1:
            self.state.log = self.state.log[:leader_prev_log_index + 1]
        # append the entries from leader's log to peer's log
        entries = message['_entries']
        for entry in entries:
            self.state.log.append(LogEntry(entry['_term_number'], entry['_command']))
        # if leader's commit index is greater than peer's commit index, then update peer's commit index
        if message['_leader_commit'] > self.state.commit_index:
            self.state.commit_index = min(message['_leader_commit'], len(self.state.log) - 1)
        print("log: {}".format(self.state.log))
        return True, self.state.current_term, None


    def redirect_message(self, message):
        print('Redirect message received')
        print(message)

    # ==================================================================================
    # RPC SENDERS
    # ==================================================================================

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
                        if 2 * self.state.total_votes > len(self.state.peers):
                            # become leader
                            return State.LEADER, self.state.current_term
        except Exception as e:
            logger.error("Error while sending request vote to peer {}: {}".format(peer, e))
        return State.CANDIDATE, self.state.current_term

    # SEND REDIRECT MESSAGE

    def send_redirect_message(self, peer, command):
        try:
            peer.send_redirect_message(command)
        except Exception as e:
            logger.error("Error while sending redirect message to peer {}: {}".format(peer, e))

    # SEND APPEND ENTRIES RPC
    def send_append_entries(self, command):
        # check if I am leader if no redirect to leader
        if self.state.state_type != State.LEADER:
            for peer in self.state.peers:
                if peer.host == self.state.leader_id[0] and peer.port == self.state.leader_id[1]:
                    return self.send_redirect_message(peer, command)
        # insert this command in the log
        log_entry = LogEntry(self.state.current_term, command)
        self.state.log.append(log_entry)
        current_index = len(self.state.log) - 1
        threads = []
        num_of_successful_replications = [1]
        for peer in self.state.peers:
            thread = threading.Thread(target=self.call_peer_append_entries, args=(peer, num_of_successful_replications))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        if 2 * num_of_successful_replications[0] > len(self.state.peers):
            self.state.commit_index = current_index
            print('Current commit index {}'.format(self.state.commit_index))
            return True
        return False

    def call_peer_append_entries(self, peer, num_of_successful_replications):
        try:
            logger.info('Sending append entries to peer {}'.format(peer))
            message = self._build_append_entries_message(peer)
            response = peer.send_append_entries(message)
            is_append_successful, peer_term_number, peer_next_index = response
            # if I am not a leader at all
            if not is_append_successful:
                if peer_term_number > self.state.current_term:
                    # demote to follower
                    self.state.state_type = State.FOLLOWER
                    # self.state.current_term = peer_term_number
                    self.change_state_properties()
                    # request forward to the true leader
                    return False
                elif peer_next_index is not None:
                    # decrement next index for this peer
                    self.state.next_index[(peer.host, peer.port)] = peer_next_index
                    self.call_peer_append_entries(peer, num_of_successful_replications)
            else:
                # increment next index for this peer
                self.state.next_index[(peer.host, peer.port)] += len(message['_entries'])
                # increment match index for this peer
                self.state.match_index[(peer.host, peer.port)] += 1
                num_of_successful_replications[0] += 1
        except Exception as e:
            logger.error('Error sending append entries to peer {}'.format(e))

    def _build_append_entries_message(self, peer):
        peer = (peer.host, peer.port)
        term = self.state.current_term
        leader_id = self.state.server_id
        prev_log_index = self.state.next_index[peer] - 1
        prev_log_term = self.state.log[prev_log_index].term_number
        entries = self.state.log[prev_log_index + 1:]
        leader_commit = self.state.commit_index
        return AppendEntriesMessage(term, leader_id, prev_log_index, prev_log_term, entries, leader_commit)

    def start_election(self):
        # upgrade state to candidate if not already candidate
        if self.state.state_type == State.FOLLOWER:
            logger.info("Upgrading state to candidate")
            self.state.state_type = State.CANDIDATE
            self.change_state_properties()
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
                self.change_state_properties()
                break
            # if majority votes for you, become leader
            elif next_state_type == State.LEADER:
                logger.info("Upgrading state to leader")
                self.state.state_type = State.LEADER
                self.state.leader_id = self.state.server_id
                self.change_state_properties()
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
