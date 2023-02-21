from message.message import Message
from message.message_type import MessageType


class AppendEntriesMessage(Message):
    """Append entries message."""

    def __init__(self, sender, receiver, term, content):
        super(AppendEntriesMessage, self).__init__(sender, receiver, content, term, MessageType.APPEND_ENTRIES)
