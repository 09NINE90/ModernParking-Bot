from enum import Enum


class ConfirmationStatus(Enum):
    CANCELLED = "CANCELLED"
    ACCEPTED = "ACCEPTED"
    WAITING = "WAITING"
    REJECTED = "REJECTED"
