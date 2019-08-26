from abc import ABC, abstractmethod
from unit import Bomb, Troop


class Order(ABC):
    def validate(self, game, team):
        """
        Validate that an order can be given, e.g. that a move command is being
        made from an owned factory.

        Parameters
        ----------
        game : GameBoard
            Current game state
        team : int
            Team issuing the command

        Returns
        -------
        bool
            True if the order can be given, False if not
        """
        # Use the template method pattern so we can preserve the docstring
        return self._validate(game, team)

    @abstractmethod
    def _validate(self, game, team):
        pass

    def execute(self, game):
        """
        Execute the order, mutating the game state.

        Parameters
        ----------
        game : GameBoard
        """
        self._execute(game)

    @abstractmethod
    def _execute(self, move):
        pass

    @classmethod
    def from_string(_, order_string):
        """
        Create an order from an order string. For example:

        "MOVE 1 2 10" --> ``Move(source=1, destination=2, count=10)``

        "BOMB 3 4" --> ``Bomb(soure=3, destination=4)``

        "INC 2" --> ``Inc(target=2)``

        "WAIT" --> ``Wait()``

        "MSG message" --> ``Msg(message="message")``

        Parameters
        ----------
        order_string : Unicode

        Raises
        ------
        ValueError
            If the order is invalid
        """
        str_order = order_string.split()[0].upper()
        str_args = order_string.split()[1:]

        args = []
        for arg in str_args:
            try:
                new_arg = int(arg)
            except ValueError:
                new_arg = arg

            args.append(new_arg)

        possible_orders = {
            "MOVE": Move,
            "BOMB": Bomb,
            "INC": Inc,
            "WAIT": Wait,
            "MSG": Msg,
        }

        if str_order in possible_orders:
            order = possible_orders[str_order]
        else:
            raise ValueError("Order {} unknown.".format(str_order))

        return order(args)


class Move(Order):
    """
    Move a number of troops from an ally factory to another factory

    Parameters
    ----------
    source : int
        Source factory ID
    destination : int
        Destination factory ID
    count : int
        Number of troops to move
    """
    def __init__(self, source, destination, count):
        self.source = source
        self.destination = destination
        self.count = count

    def _validate(self, game, team):
        source_factory = game.get_factory(self.source)
        target_factory = game.get_factory(self.destination)

        if team == game.get_factory(self.source).team \
                and source_factory.id != target_factory.id:
            return True
        else:
            return False

    def _execute(self, game):
        source_factory = game.get_factory(self.source)
        troop_strength = min(source_factory.stock, self.count)

        if troop_strength == 0:
            return

        source_factory.stock -= troop_strength

        target_factory = game.get_factory(self.destination)

        new_troop = Troop(troop_strength, source_factory, target_factory)
        game.troops.append(new_troop)


class SendBomb(Order):
    """
    Send a bomb from an ally factory to an enemy factory

    Parameters
    ----------
    source : int
        Source factory ID
    destination : int
        Destination factory ID
    """
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def _validate(self, game, team):
        source_factory = game.get_factory(self.source)
        target_factory = game.get_factory(self.destination)

        different_factory = source_factory.id != target_factory.id
        right_team = team == game.get_factory(self.source).team
        enough_bombs = game.remaining_bombs[team] > 0

        if right_team and enough_bombs and different_factory:
            return True
        else:
            return False

    def _execute(self, game):
        factory = game.get_factory(self.source)
        target = game.get_factory(self.destination)

        game.remaining_bombs[factory.team] -= 1
        new_bomb = Bomb(None, factory, target)
        game.bombs.append(new_bomb)


class Inc(Order):
    """
    Increase production of an ally factory at the cost of 10 troops

    Parameters
    ----------
    target : int
        Factory to upgrade
    """
    def __init__(self, target):
        self.target = target

    def _validate(self, game, team):
        if team == game.get_factory(self.target).team:
            return True
        else:
            return False

    def _execute(self, game):
        factory = game.get_factory(self.target)
        factory.upgrade()


class Wait(Order):
    """
    Do nothing
    """
    def __init__(self):
        pass

    def _validate(self, game, team):
        return True

    def _execute(self, game):
        pass


class Msg(Order):
    """
    Create an ingame message

    Parameters
    ----------
    message : Unicode
        Message to send
    """
    def __init__(self, message):
        self.message = message

    def _validate(self, game, team):
        return True

    def _execute(self, game):
        pass  # TODO: implement
