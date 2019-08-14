import itertools
import math
import random
import numpy as np


class GameBoard:
    def __init__(self):
        self.factories = []
        self.links = []
        self.troops = []
        self.bombs = []
        self.orders = {
            -1: [],
            1: [],
        }
        self.game_over = False

    def init_game(
            self,
            num_factory_range=(7, 15),
            min_dist=1,
            max_dist=20,
            stock_range_player=(15, 30),
            stock_range_neutral=(0, 10),):
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
                Factory(
                    id=0,
                    team=0,
                    production=random.randint(0, 3),
                    stock=self.random_stock(neutral=True),
                    position=(0, 0),
                )
            )

        def new_factory_pair(neutral):
            # Generate a new factory in one hemisphere.
            dist = random.random() * self.max_dist/2.0
            angle = random.random() * math.pi

            pos_x = math.cos(angle) * dist
            pos_y = math.sin(angle) * dist

            stock = self.random_stock(neutral=neutral)
            production = random.randint(0, 3)

            team = 0 if neutral else 1

            start_id = len(self.factories)
            new_factory = Factory(
                id=start_id,
                team=team,
                production=production,
                stock=stock,
                position=(pos_x, pos_y)
            )
            rotated_factory = Factory(
                id=start_id+1,
                team=-team,
                production=production,
                stock=stock,
                position=(-pos_x, -pos_y)
            )

            return [new_factory, rotated_factory]

        def all_links_ok(factories):
            """
            Returns true if all distances are between min_dist and max_dist.
            TODO: This is a very lazy implementation that should be improved.
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
        self.links = []
        for a, b in itertools.combinations(self.factories, 2):
            dist = factory_dist(a, b)
            self.links.append(
                (a.id, b.id, dist)
            )
            self.links.append(
                (b.id, a.id, dist)
            )

    def random_stock(self, neutral):
        if neutral:
            return random.randint(*self.stock_range_neutral)
        else:
            return random.randint(*self.stock_range_player)

    def update(self):
        for troop in self.troops:
            troop.move()
        self.troops = [troop for troop in self.troops if troop.active]
        for bomb in self.bombs:
            bomb.move()
        self.bombs = [bomb for bomb in self.bombs if bomb.active]
        for order in self.orders:
            self.execute(order)
        for factory in self.factories:
            factory.produce()
            factory.resolve_battles()
            factory.resolve_bombs()
        if self.end_conditions():
            self.game_over = True


def factory_dist(a, b):
    float_dist = math.sqrt(
        (a.position[0]-b.position[0])**2 + (a.position[1]-b.position[1])**2
    )
    return int(float_dist)


class Factory:
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
        occupying_result = self.occupying_troops[self.team] \
                         - self.occupying_troops[-self.team]

        self.stock += occupying_result

        if self.stock == 0:
            self.team = 0
        elif self.stock < 0:
            self.team = -self.team
            self.stock = -self.stock

        self.occupying_troops = {-1: 0, 1: 0}

    def resolve_bombs(self):
        for _ in range(self.bombs_arriving):
            destroyed = max(10, self.stock//2)
            self.stock -= destroyed

        self.bombs_arriving = 0


class Unit:
    def __init__(self, strength, source, destination):
        self.strength = strength

        self.team = self.source.team
        self.active = True

        # N.B. implement a jsonize that just outputs source, dest IDs
        self.source = source
        self.destination = destination

        self.distance = factory_dist(source, destination)
        self.travelled = 0

    def resolve_at_dest(self):
        # TODO: make this class abstract so we don't have this lazy error
        raise NotImplementedError("Spawn Troops or Bombs, not Units.")

    def move(self):
        self.travelled += 1
        if self.travelled == self.distance:
            self.resolve_at_dest()
            self.active = False

    def get_position(self):
        vec = np.array(self.destination.position) \
            - np.array(self.source.position)

        vec *= self.travelled / self.distance

        return vec


class Troop(Unit):
    def resolve_at_dest(self):
        self.destination.occupying_troops[self.team] += self.strength


class Bomb(Unit):
    def resolve_at_dest(self):
        self.destination.bombs_arriving += 1
