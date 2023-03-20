class LogEntry:
    def __init__(self, term, command):
        self._term_number = term
        self._command = command

    @property
    def term_number(self):
        return self._term_number

    @property
    def command(self):
        return self._command