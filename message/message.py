import time


class Message(object):

    def __init__(self, sender, receiver, content, term, message_type):
        self._sender = sender
        self._receiver = receiver
        self._content = content
        self._timestamp = time.time()
        self._term = term
        self._type = message_type

    def __str__(self):
        return "Message from %s to %s" % (self._sender, self._receiver)

    def __repr__(self):
        return "<Message from %s to %s>" % (self._sender, self._receiver)

    @property
    def sender(self):
        return self._sender

    @property
    def receiver(self):
        return self._receiver

    @property
    def content(self):
        return self._content

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def term(self):
        return self._term

    @property
    def type(self):
        return self._type
