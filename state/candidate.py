from .state import State


class Candidate(State):

    def __init__(self, server_ip_address,  log, peers):
        super().__init__(server_ip_address, log, peers)

    def start_election(self):
        print("Starting election for term {}".format(self._current_term))
        # set current term
        self._current_term += 1
        # vote for self
        self._voted_for[self.current_term] = self.server_id
        # reset election timeout
        # send request vote RPCs to all other servers
        for peer in self.peers:
            print("Sending request vote to {}".format(peer))
            try:
                vote = peer.send_request_vote(self.current_term, self.server_id)
                print(vote)
            except Exception as e:
                print("Error sending request vote to {}: {}".format(peer, e))
                continue



