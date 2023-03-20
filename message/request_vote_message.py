from message.message import Message


class RequestVoteMessage(Message):
    """Request vote message."""

    def __init__(self, term, content):
        super(RequestVoteMessage, self).__init__(term, content)
        self._candidate_id = content['candidate_id']
        self._last_log_index = content['last_log_index']
        self._last_log_term = content['last_log_term']


    @property
    def candidate_id(self):
        return self._candidate_id

    @property
    def last_log_index(self):
        return self._last_log_index

    @property
    def last_log_term(self):
        return self._last_log_term

    def __str__(self):
        return "RequestVote" + super(RequestVoteMessage, self).__str__()

    def __repr__(self):
        return self.__str__()