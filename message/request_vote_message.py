from message.message import Message
from message.message_type import MessageType


class RequestVoteMessage(Message):
    """Request vote message."""

    def __init__(self, sender, receiver, term, content):
        super(RequestVoteMessage, self).__init__(sender, receiver, content, term, MessageType.REQUEST_VOTE)