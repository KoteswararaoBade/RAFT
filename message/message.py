import time


class Message(object):

    def __init__(self, term, content):
        self._term_number = term
        self._content = content
        self._timestamp = time.time()

    def __str__(self):
        return "Message(content=%s, term=%s, timestamp=%s)" % (self._content, self._term_number, self._timestamp)

    def __repr__(self):
        return self.__str__()

    @property
    def content(self):
        return self._content

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def term_number(self):
        return self._term_number
