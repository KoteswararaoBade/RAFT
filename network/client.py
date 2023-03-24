from util.rpcutil import RPCClient


class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._rpc = RPCClient(host, port)

    def send_request_vote(self, message):
        return self._rpc.call("request_vote", message)

    def send_heart_beat(self, leader_id, term):
        return self._rpc.call("heart_beat", leader_id, term)

    def send_append_entries(self, message):
        return self._rpc.call("append_entries", message)

    def send_redirect_message(self, message):
        return self._rpc.call("redirect_message", message)

    def get(self, key):
        return self._rpc.call("get", key)

    def set(self, key, value):
        return self._rpc.call("set", key, value)

    def __str__(self):
        return "Client(host=%s, port=%s)" % (self.host, self.port)
