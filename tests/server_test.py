import random
import time
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer

from state.state import State


class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


# sleep for random number of seconds
def sleep():
    r = random.randint(2, 10)
    print('sleeping {} seconds'.format(r))
    time.sleep(r)
    return 'slept {} seconds, exiting'.format(r)


# run server
def run_server(host="localhost", port=8000):
    follower1 = State(host, port, None)
    follower1.start()
    follower1.start_timer()


if __name__ == '__main__':
    run_server()
