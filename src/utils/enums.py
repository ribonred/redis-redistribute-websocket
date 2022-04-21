from enum import Enum


class Status(Enum):
    """
    Enum class for status
    """

    SUCCESS = "success"
    ERROR = "error"
    SUBSCRIBTION = "subscription"
    QUOTES = "q"
    TRADES = "t"
    DAYS = "d"
    MINUTES = "b"


class Action(Enum):
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
