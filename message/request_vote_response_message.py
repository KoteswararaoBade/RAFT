from message.message import Message
from message.message_type import MessageType


class RequestVoteResponseMessage(Message):
    """Request vote reponse message."""

    def __init__(self, sender, receiver, term, content):
        super(RequestVoteResponseMessage, self).__init__(sender, receiver, content, term, MessageType.REQUEST_VOTE)
