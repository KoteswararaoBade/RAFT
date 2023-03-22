import time


class Message(object):

    def __init__(self, term):
        self._term_number = term
        self._timestamp = time.time()

    def __str__(self):
        return "Message(term=%s, timestamp=%s)" % (self._term_number, self._timestamp)

    def __repr__(self):
        return self.__str__()

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def term_number(self):
        return self._term_number
