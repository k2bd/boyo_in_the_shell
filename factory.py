import math


def factory_dist(a, b):
    """
    Return the number of turns it takes a unit to get between two factories

    Parameters
    ----------
    a : Factory
    b : Factory
    """
    float_dist = math.sqrt(
        (a.position[0]-b.position[0])**2 + (a.position[1]-b.position[1])**2
    )
    return int(float_dist)


class Factory:
    """
    Game Factory

    Parameters
    ----------
    fid : int
        ID of this factory. Should be unique.
    team : int
        -1 or 1 for players, 0 for neutral
    production : int
        Per-turn stock production
    stock : int
        Initial army stock
    position : (float, float)
        x and y coordinates of this base
    """
    def __init__(self, fid, team, production, stock, position):
        self.id = fid

        self.team = team
        self.stock = stock
        self.position = position  # (x, y)

        self.production = production

        # List holding net strength of troops that have moved into the factory
        # this turn
        self.occupying_troops = {
            -1: 0,
            1: 0,
        }

        # Number of bombs currently arriving
        self.bombs_arriving = 0

    def produce(self):
        if self.team == 0:
            return
        self.stock += self.production

    def resolve_battles(self):
        occupying_result = self.occupying_troops[1] - self.occupying_troops[-1]
        if occupying_result > 0:
            winner = 1
        elif occupying_result < 0:
            winner = -1
        else:
            winner = None
        occupying_result = abs(occupying_result)

        if self.team == winner:
            self.stock += occupying_result
        else:
            self.stock -= occupying_result

        if self.stock < 0:
            self.team = winner
            self.stock = abs(self.stock)

        self.occupying_troops = {-1: 0, 1: 0}

    def resolve_bombs(self):
        for _ in range(self.bombs_arriving):
            destroyed = max(10, self.stock//2)
            self.stock -= destroyed

        self.bombs_arriving = 0
