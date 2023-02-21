import os
import threading
import time
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer

from util.rpcutil import RPCServer
from util.loggingutil import LoggingUtil

logger = LoggingUtil(os.path.basename(__file__)).get_logger()


class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class Server(RPCServer):

    def __init__(self, server_id, host, port):
        super().__init__(host, port)
        self._id = server_id
        self._data = {}

    def start(self):
        ip, port = self._server.server_address
        logger.info("Starting network at %s:%s" % (ip, port))
        # Start a thread with the network -- that thread will then start one
        # more thread for each request
        # super(Server, self).start()
        server_thread = threading.Thread(target=super(Server, self).start)
        # Exit the network thread when the main thread terminates
        # server_thread.daemon = True
        server_thread.start()
        logger.info("Server loop running in thread: %s" % server_thread.name)

    def stop(self):
        self.server.stop()

    def request_vote(self, term_number, candidate_id):
        print('Received vote request from {} with term number {}'.format(candidate_id, term_number))
        return True

    def get(self, key):
        logger.info("get(%s)" % key)
        if self.exists(key):
            return self._data[key]
        else:
            return None

    def set(self, key, value):
        self._data[key] = value

    def delete(self, key):
        del self._data[key]

    def exists(self, key):
        return key in self._data

    def keys(self):
        return list(self._data.keys())


def main():
    server = Server(1, 'localhost', 8080)
    try:
        server.start()
    except KeyboardInterrupt as e:
        print(e)
        server.stop()


if __name__ == '__main__':
    main()
