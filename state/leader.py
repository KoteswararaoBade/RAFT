from state.state import State


class Leader(State):

    def __init__(self, server_ip_address, log, peers):
        super().__init__(server_ip_address, log, peers)