from message.message import Message
from message.message_type import MessageType


class ResponseMessage(Message):
    """Response message."""

    def __init__(self, term):
        super(ResponseMessage, self).__init__(term)
