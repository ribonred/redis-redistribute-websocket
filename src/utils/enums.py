from enum import Enum


class Status(Enum):
    """
    Enum class for status
    """

    SUCCESS = "success"
    ERROR = "error"
    SUBSCRIBTION = "subscription"
    QUOTES = "q"


class Action(Enum):
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
