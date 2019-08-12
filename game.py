import itertools
import math
import random


class GameBoard:
    def __init__(
            self,
            num_factory_range=(7, 15),
            min_dist=1,
            max_dist=20,
            stock_range_player=(15, 30),
            stock_range_neutral=(0, 10),):
        self.factories = []
        self.links = []
        self.troops = []

        self.num_factories = random.randint(*num_factory_range)
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.stock_range_player = stock_range_player
        self.stock_range_neutral = stock_range_neutral

        self.place_factories()
        self.link_factories()

    def place_factories(self):
        """
        Randomize the factory locations, respecting min and max distances.
        Enforce rotational symmetry. If we have an odd number of factories
        place a neutral one in the middle.
        """
        if self.num_factories % 2 == 1:
            self.factories.append(
                Factory(0, self.random_stock(neutral=True), (0, 0))
            )

        def new_factory_pair(neutral):
            # Generate a new factory in one hemisphere.
            dist = random.random() * self.max_dist/2.0
            angle = random.random() * math.pi

            pos_x = math.cos(angle) * dist
            pos_y = math.sin(angle) * dist

            stock = self.random_stock(neutral=neutral)

            team = 0 if neutral else 1

            new_factory = Factory(
                team, stock, (pos_x, pos_y)
            )
            rotated_factory = Factory(
                -team, stock, (-pos_x, -pos_y)
            )

            return [new_factory, rotated_factory]

        def all_links_ok(factories):
            """ Returns true if all distances are between min_dist and max_dist
            """
            for a, b in itertools.combinations(factories, 2):
                if not self.min_dist < factory_dist(a, b) < self.max_dist:
                    return False
            return True

        # Randomize player bases
        while len(self.factories) < 3:
            factories = self.factories + new_factory_pair(neutral=False)
            if all_links_ok(factories):
                self.factories = factories

        # Fill the rest with neutrals
        while len(self.factories) < self.num_factories:
            factories = self.factories + new_factory_pair(neutral=True)
            if all_links_ok(factories):
                self.factories = factories

    def link_factories(self):
        pass

    def random_stock(self, neutral):
        if neutral:
            return random.randint(*self.stock_range_neutral)
        else:
            return random.randint(*self.stock_range_player)


def factory_dist(a, b):
    float_dist = math.sqrt(
        (a.position[0]-b.position[0])**2 + (a.position[1]-b.position[1])**2
    )
    return int(float_dist)


class Factory:
    def __init__(self, team, stock, position):
        self.team = team
        self.stock = stock
        self.position = position  # (x, y)


class Troop:
    def __init__(self, strength, source, destination):
        self.strength = strength
        self.source = source
        self.destination = destination
        self.orig_dist = 0
        self.distance = self.orig_dist
