import functools
import unittest

from factory import Factory, factory_dist


class TestFactoryDist(unittest.TestCase):
    def test_factory_dist(self):
        fact = functools.partial(Factory, 0, 0, 0, 0)

        a = fact(position=(0, 0))
        b = fact(position=(0, 1))
        self.assertEqual(1, factory_dist(a, b))
        self.assertEqual(0, factory_dist(b, b))

        a = fact(position=(-1, -1))
        b = fact(position=(1, 1))
        self.assertEqual(2, factory_dist(a, b))

        a = fact(position=(0, 0))
        b = fact(position=(0, 0.5))
        self.assertEqual(0, factory_dist(a, b))


class TestFactory(unittest.TestCase):
    def test_produce(self):
        for team in [-1, 1]:
            team_factory = Factory(0, team, 3, 10, (0, 0))
            team_factory.produce()
            self.assertEqual(13, team_factory.stock)

            zero_prod_fac = Factory(0, team, 0, 10, (0, 0))
            zero_prod_fac.produce()
            self.assertEqual(10, zero_prod_fac.stock)

        # Neutral factories don't produce
        neutral_factory = Factory(0, 0, 3, 10, (0, 0))
        neutral_factory.produce()
        self.assertEqual(10, neutral_factory.stock)

    def test_resolve_battles(self):
        # (Factory, occupying_troops, expt_team, expt_stock)
        test_battles = [
            # Neutral factory with no troops can be taken over
            (Factory(0, 0, 0, 0, (0, 0)), {-1: 0, 1: 1}, 1, 1),
            (Factory(0, 0, 0, 0, (0, 0)), {-1: 2, 1: 1}, -1, 1),
            # Neutral factory with no troops, stalemate doesn't change team
            (Factory(0, 0, 0, 0, (0, 0)), {-1: 1, 1: 1}, 0, 0),
            # Team factory changes hands on loss
            (Factory(0, 1, 0, 10, (0, 0)), {-1: 20, 1: 5}, -1, 5),
            (Factory(0, -1, 0, 10, (0, 0)), {-1: 5, 1: 20}, 1, 5),
            # Team factory with 0 resulting troops doesnt change hands
            (Factory(0, 1, 0, 10, (0, 0)), {-1: 10, 1: 0}, 1, 0),
            (Factory(0, -1, 0, 10, (0, 0)), {-1: 0, 1: 10}, -1, 0),
            # Reinforcement
            (Factory(0, 1, 0, 5, (0, 0)), {-1: 10, 1: 20}, 1, 15),
            (Factory(0, -1, 0, 5, (0, 0)), {-1: 20, 1: 10}, -1, 15),
        ]

        for factory, occupying_troops, expt_team, expt_stock in test_battles:
            factory.occupying_troops = occupying_troops
            factory.resolve_battles()

            self.assertEqual(factory.team, expt_team)
            self.assertEqual(factory.stock, expt_stock)

            # Reset occupiers
            self.assertEqual(
                factory.occupying_troops, {-1: 0, 1: 0}
            )

    def test_resolve_bombs(self):
        # (Factory, bombs_arriving, expt_stock)
        test_bombs = [
            # Bombs take out half of the factory's stock
            (Factory(0, 1, 0, 33, (0, 0)), 1, 17),
            # Bombs take out minimum 10 stock
            (Factory(0, -1, 0, 13, (0, 0)), 1, 3),
            # Multiple bombs stack properly
            (Factory(0, 0, 0, 33, (0, 0)), 2, 7),
            # Can't go below zero
            (Factory(0, 1, 0, 5, (0, 0)), 2, 0),
        ]

        for factory, bombs_arriving, expt_stock in test_bombs:
            orig_team = factory.team
            factory.bombs_arriving = bombs_arriving
            factory.resolve_bombs()

            self.assertEqual(factory.team, orig_team)
            self.assertEqual(factory.stock, expt_stock)
            self.assertEqual(factory.disabled_turns, 5)

            self.assertEqual(factory.bombs_arriving, 0)

    def test_bombs_disable_production(self):
        team_factory = Factory(0, 1, 3, 10, (0, 0))
        team_factory.bombs_arriving = 1
        team_factory.resolve_bombs()

        # Bomb a factory again while producing
        again_bombed = Factory(0, -1, 3, 10, (0, 0))
        again_bombed.bombs_arriving = 1
        again_bombed.resolve_bombs()

        # Disable neutral factory then take it over
        captured_factory = Factory(0, 0, 3, 10, (0, 0))
        captured_factory.bombs_arriving = 1
        captured_factory.resolve_bombs()

        for i in range(5):
            team_factory.produce()
            captured_factory.produce()
            again_bombed.produce()
            self.assertEqual(0, team_factory.stock)
            self.assertEqual(4-i, team_factory.disabled_turns)
            self.assertEqual(0, again_bombed.stock)
            self.assertEqual(0, captured_factory.stock)
            self.assertEqual(4-i, captured_factory.disabled_turns)

            # Captured here
            if i == 2:
                captured_factory.team = -1
                again_bombed.bombs_arriving = 1
                again_bombed.resolve_bombs()

        team_factory.produce()
        self.assertEqual(3, team_factory.stock)

        captured_factory.produce()
        self.assertEqual(3, captured_factory.stock)

        again_bombed.produce()
        self.assertEqual(0, again_bombed.stock)
        self.assertEqual(2, again_bombed.disabled_turns)

    def test_upgrade(self):
        factory_a = Factory(0, 1, 0, 10, (0, 0))
        factory_b = Factory(0, 1, 2, 11, (0, 0))
        factory_c = Factory(0, 1, 0, 9, (0, 0))
        factory_d = Factory(0, 1, 3, 11, (0, 0))

        factory_a.upgrade()
        self.assertEqual(0, factory_a.stock)
        self.assertEqual(1, factory_a.production)

        factory_b.upgrade()
        self.assertEqual(1, factory_b.stock)
        self.assertEqual(3, factory_b.production)

        factory_c.upgrade()
        self.assertEqual(9, factory_c.stock)
        self.assertEqual(0, factory_c.production)

        factory_d.upgrade()
        self.assertEqual(11, factory_d.stock)
        self.assertEqual(3, factory_d.production)
