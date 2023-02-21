from message.message import Message
from message.message_type import MessageType


class ResponseMessage(Message):
    """Response message."""

    def __init__(self, sender, receiver, term, content):
        super(ResponseMessage, self).__init__(sender, receiver, content, term, MessageType.RESPONSE)
