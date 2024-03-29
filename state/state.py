import random
import time

from log.log import LogEntry
from network.server import Server
from network.client import Client


class State:

    LEADER = 'leader'
    FOLLOWER = 'follower'
    CANDIDATE = 'candidate'

    def __init__(self, server_ip_address, peers, state_type):
        # peer information
        self._server_id = server_ip_address
        self._peers = [Client(peer[0], peer[1]) for peer in peers]
        self._leader_id = None
        # persistent state
        self._log = [LogEntry(0, None)]
        self._voted_for = {}
        self._current_term = 0
        # volatile state
        self._commit_index = 0
        self._last_applied = 0
        self._total_votes = 0

        # variable to keep track of state
        self._state_type = None

        # leader state
        self._next_index = {(peer[0], peer[1]): len(self.log) for peer in peers}
        self._match_index = {(peer[0], peer[1]): 0 for peer in peers}

    @property
    def state_type(self):
        return self._state_type

    @state_type.setter
    def state_type(self, state_type):
        self._state_type = state_type

    @property
    def leader_id(self):
        return self._leader_id

    @leader_id.setter
    def leader_id(self, leader_id):
        self._leader_id = leader_id

    @property
    def voted_for(self):
        return self._voted_for

    @voted_for.setter
    def voted_for(self, voted_for):
        self._voted_for = voted_for

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, log):
        self._log = log

    @property
    def peers(self):
        return self._peers

    @peers.setter
    def peers(self, peers):
        self._peers = peers

    @property
    def current_term(self):
        return self._current_term

    @current_term.setter
    def current_term(self, current_term):
        self._current_term = current_term

    @property
    def server_id(self):
        return self._server_id

    @property
    def total_votes(self):
        return self._total_votes

    @total_votes.setter
    def total_votes(self, total_votes):
        self._total_votes = total_votes

    @property
    def commit_index(self):
        return self._commit_index

    @commit_index.setter
    def commit_index(self, commit_index):
        self._commit_index = commit_index

    @property
    def last_applied(self):
        return self._last_applied

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


    def set_all_properties(self, state):
        self._current_term = state.current_term
        self._voted_for = state.voted_for
        self._leader_id = state.leader_id
        self._log = state.log
        self._peers = state.peers
        self._server_id = state.server_id
        self._total_votes = state.total_votes
        self._commit_index = state.commit_index
        self._last_applied = state.last_applied

    def __str__(self):
        return "State: current_term: {}, voted_for: {}, leader_id: {}".format(self._current_term, self._voted_for,
                                                                              self._leader_id)
