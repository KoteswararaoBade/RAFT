import random
import time

from network.server import Server
from network.client import Client


class State:

    def __init__(self, server_ip_address, log, peers):
        self._server_id = server_ip_address
        self._voted_for = {}
        self._leader_id = None
        self._log = log
        self._peers = [Client(peer[0], peer[1]) for peer in peers]
        self._current_term = 0

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

    def set_all_properties(self, state):
        self._current_term = state.current_term
        self._voted_for = state.voted_for
        self._leader_id = state.leader_id
        self._log = state.log
        self._peers = state.peers
        self._server_id = state.server_id

    def __str__(self):
        return "State: current_term: {}, voted_for: {}, leader_id: {}".format(self._current_term, self._voted_for,
                                                                              self._leader_id)
