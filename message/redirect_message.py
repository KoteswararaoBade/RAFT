from message.message import Message


class RedirectMessage(Message):
    """Request vote message."""

    def __init__(self, term, command):
        super(RedirectMessage, self).__init__(term)
        self._command = command

    @property
    def command(self):
        return self._command

    def __str__(self):
        return "RedirectMessage[ command: %s ]" % self.command

