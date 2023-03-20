from message.message import Message
from message.message_type import MessageType


class AppendEntriesMessage(Message):
    """Append entries message."""

    def __init__(self, term, content):
        super(AppendEntriesMessage, self).__init__(term, content)
