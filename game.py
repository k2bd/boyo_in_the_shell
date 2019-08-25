import itertools
import math
import random

from factory import Factory, factory_dist


class GameBoard:
    """
    A game board for Boyo in the Shell.

    Game loop with:

    while not game_board.game_over:
        game_board.update()
    """
    def __init__(self):
        self.factories = []
        self.links = []
        self.troops = []
        self.bombs = []
        self.remaining_bombs = {-1: 2, 1: 2}
        self.orders = {-1: [], 1: []}
        self.game_over = False
        self.max_turns = None
        self.current_turn = 0

    def init_game(
            self,
            num_factory_range=(7, 15),
            min_dist=1,
            max_dist=20,
            stock_range_player=(15, 30),
            stock_range_neutral=(0, 10),
            max_turns=200):
        self.num_factories = random.randint(*num_factory_range)
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.stock_range_player = stock_range_player
        self.stock_range_neutral = stock_range_neutral
        self.max_turns = max_turns

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
        """
        Create a list of factory-factory distances, mainly for exporting to
        JSON
        """
        self.links = []
        for a, b in itertools.combinations(self.factories, 2):
            dist = factory_dist(a, b)
            self.links.append(
                (a.id, b.id, dist)
            )
            self.links.append(
                (b.id, a.id, dist)
            )

    def get_factory(self, factory_id):
        """
        Get a factory with the given ID

        Parameters
        ----------
        factory_id : int
        """
        for factory in self.factories:
            if factory.id == factory_id:
                return factory
        else:
            msg = "Factory {} not found"
            raise ValueError(msg.format(factory_id))

    def random_stock(self, neutral):
        """
        Convenience method to return a random stock
        """
        if neutral:
            return random.randint(*self.stock_range_neutral)
        else:
            return random.randint(*self.stock_range_player)

    def update(self):
        """
        Execute game logic for one turn
        """
        self.current_turn += 1

        for troop in self.troops:
            troop.move()

        self.troops = [troop for troop in self.troops if troop.active]

        for bomb in self.bombs:
            bomb.move()
        self.bombs = [bomb for bomb in self.bombs if bomb.active]

        for team, orders in self.orders.items():
            for order in orders:
                if order.validate(self, team):
                    order.execute(self)

        for factory in self.factories:
            factory.produce()
            factory.resolve_battles()
            factory.resolve_bombs()

        self.check_end_conditions()

    def check_end_condition(self):
        fac_teams = [fac.team for fac in self.factories]

        if all([team == 1 for team in fac_teams]):
            self.winner = 1
            self.game_over = True
        elif all([team == -1 for team in fac_teams]):
            self.winner = -1
            self.game_over = True

        if self.max_turns is not None and self.current_turn >= self.max_turns:
            self.game_over = True

            team_facs = {
                team: len([fac for fac in self.factories if fac.team == team])
                for team in [-1, 1]
            }

            if team_facs[-1] > team_facs[1]:
                self.winner = -1
            elif team_facs[1] > team_facs[1]:
                self.winner = 1
            else:
                self.winner = 0
