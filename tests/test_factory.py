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
        for i in range(3):
            team_factory = Factory(0, 1, i, 10, (0, 0))
            team_factory.produce()
            self.assertEqual(10+i, team_factory.stock)

        # Neutral factories don't produce
        neutral_factory = Factory(0, 0, 3, 10, (0, 0))
        neutral_factory.produce()
        self.assertEqual(10, neutral_factory.stock)

    def test_resolve_battles(self):
        pass
