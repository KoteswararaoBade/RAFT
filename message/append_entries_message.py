from message.message import Message

class AppendEntriesMessage(Message):
    """Append entries message."""

    def __init__(self, term, leader_id, prev_log_index, prev_log_term, entries, leader_commit):
        super(AppendEntriesMessage, self).__init__(term)
        self._leader_id = leader_id
        self._prev_log_index = prev_log_index
        self._prev_log_term = prev_log_term
        self._entries = entries
        self._leader_commit = leader_commit

    @property
    def leader_id(self):
        return self._leader_id

    @property
    def prev_log_index(self):
        return self._prev_log_index

    @property
    def prev_log_term(self):
        return self._prev_log_term

    @property
    def entries(self):
        return self._entries

    @property
    def leader_commit(self):
        return self._leader_commit

    def __str__(self):
        return "AppendEntriesMessage[ leader id: %s, prev log index: %s, prev log term: %s, entries: %s, leader commit: %s ]" % (self.leader_id, self.prev_log_index, self.prev_log_term, self.entries, self.leader_commit)

    def __repr__(self):
        return self.__str__()