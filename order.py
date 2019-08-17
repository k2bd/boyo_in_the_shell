class Order:
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


class Bomb(Order):
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


class Inc(Order):
    """
    Increase production of an ally factory at the cost of 10 troops

    Parameters
    ----------
    target : int
        Factory to upgrade
    """
    def __init__(self, target):
        self.target = None


class Wait(Order):
    """
    Do nothing
    """
    def __init__(self):
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
