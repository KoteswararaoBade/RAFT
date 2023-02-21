import random
import threading
import time

from network.server import Server
from state.follower import Follower
from state.candidate import Candidate


def get_random_election_timeout(start, end):
    return random.randint(start, end) / 1000


class ConsensusModule:

    def __init__(self, host, port, peers):
        self.server = Server(1, host, port)
        self.state = Follower((host, port), [], peers)

    def start(self):
        self.server.start()
        self.start_timer()

    def start_election(self):
        # upgrade state to candidate if not already candidate
        if isinstance(self.state, Follower):
            old_state = self.state
            self.state = Candidate(None, [], [])
            self.state.set_all_properties(old_state)
        # send request vote to all peers
        self.state.start_election()
        # if majority votes for you, become leader
        # else, start new election

    def start_timer(self):
        election_time_out = get_random_election_timeout(5000, 8000)
        sleep_time = 0.2
        print("Starting timer", election_time_out)
        latest_timestamp = time.time()
        while (time.time() - latest_timestamp) < election_time_out:
            time.sleep(sleep_time)
        print("Election timeout reached, starting election")
        # start election on new thread
        t = threading.Thread(target=self.start_election)
        t.start()
        self.start_timer()


if __name__ == '__main__':
    consensus = ConsensusModule('10.181.88.145', 8080, [('10.181.91.9', 8080)])
    consensus.start()
