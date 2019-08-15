from enum import Enum, auto


class Order(Enum):
    MOVE = auto()
    BOMB = auto()
    INC = auto()
    WAIT = auto()
    MSG = auto()


class GameMove:
    def __init__(self, team, command, target, destination):
        if not isinstance(command, Order):
            msg = "Command {} not supported"
            raise ValueError(msg.format(command))
