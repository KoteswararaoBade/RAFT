from enum import Enum


class MessageType(Enum):
    """Message type enumeration."""
    REQUEST_VOTE = 0
    REQUEST_VOTE_RESPONSE = 1
    APPEND_ENTRIES = 2
    RESPONSE = 3

