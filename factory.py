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
        self.disabled_turns = 0

        # List holding net strength of troops that have moved into the factory
        # this turn
        self.occupying_troops = {
            -1: 0,
            1: 0,
        }

        # Number of bombs currently arriving
        self.bombs_arriving = 0

    def produce(self):
        """
        Increase the factory's stock by its production if it's not disabled.
        Reduce disable timer if disabled.
        """
        if self.disabled_turns:
            self.disabled_turns -= 1
            return

        if self.team == 0:
            return

        self.stock += self.production

    def resolve_battles(self):
        """
        Resolve battles. First, incoming troops fight. Then, any remaining
        troops reach the factory. If the factory goes below zero stock, its
        team switches to the attacking player's team.
        """
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
        """
        Resolve bombs that have arrived this turn. Bombs remove half the stock
        of the factory, minimum 10. Bombs cannot capture so the most they can
        do is reduce a factory to 0 troops.
        """
        for _ in range(self.bombs_arriving):
            destroyed = max(10, self.stock//2)
            self.stock -= destroyed
            # Can't go negative
            self.stock = max(0, self.stock)
            # Disable the factory for 5 turns
            self.disabled_turns = 5

        self.bombs_arriving = 0

    def upgrade(self):
        """
        If there's enough stock and the factory isn't at max production,
        upgrade for the cost of 10 stock.
        """
        if self.stock >= 10 and self.production < 3:
            self.stock -= 10
            self.production += 1
