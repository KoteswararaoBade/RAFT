import os
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer
from util.loggingutil import LoggingUtil
import xmlrpc  # import xmlrpc.network in Python 3

logger = LoggingUtil(os.path.basename(__file__)).get_logger()


class RPCClient(object):
    def __init__(self, host, port):
        self._server = xmlrpc.client.ServerProxy("http://%s:%s" % (host, port))

    def call(self, method, *args):
        return getattr(self._server, method)(*args)


class RPCServer(object):
    def __init__(self, host, port):
        self._server = SimpleThreadedXMLRPCServer((host, port), allow_none=True)
        self._server.register_instance(self)

    def start(self):
        logger.info("Server started.")
        self._server.serve_forever()

    def stop(self):
        logger.info("Server stopped.")
        self._server.shutdown()

    @property
    def server(self):
        return self._server


class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass
