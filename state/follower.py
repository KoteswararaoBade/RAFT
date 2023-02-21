import random
import time

from network.server import Server
from state.state import State


def get_random_election_timeout(start, end):
    return random.randint(start, end) / 1000


class Follower(State):

    def __init__(self, server_ip_address, log, peers):
        super().__init__(server_ip_address, log, peers)

    def join_cluster(self):
        pass
