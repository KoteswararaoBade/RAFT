from message.message import Message
from message.message_type import MessageType


class RequestVoteResponseMessage(Message):
    """Request vote reponse message."""

    def __init__(self, term):
        super(RequestVoteResponseMessage, self).__init__(term)
