import unittest

import numpy as np

from factory import Factory, factory_dist
from unit import Unit, Bomb, Troop


class TestUnits(unittest.TestCase):
    def test_cannot_init_base_unit(self):
        with self.assertRaises(TypeError) as err:
            Unit(1, None, None)

        self.assertIn(
            "Can't instantiate abstract",
            str(err.exception)
        )

    def test_units_move(self):
        unit_types = [Bomb, Troop]

        for unit_type in unit_types:
            source_fac = Factory(0, 1, 0, 0, (15, -10))
            dest_fac = Factory(1, 1, 0, 0, (-5, 20))

            unit = unit_type(10, source_fac, dest_fac)

            np.testing.assert_allclose(
                unit.get_position(),
                source_fac.position
            )
            self.assertTrue(unit.active)

            total_dist = factory_dist(source_fac, dest_fac)

            for i in range(1, total_dist):
                unit.move()
                self.assertEqual(i, unit.travelled)
                self.assertTrue(unit.active)
                # TODO: test position

            unit.move()
            self.assertFalse(unit.active)
            np.testing.assert_allclose(
                unit.get_position(),
                dest_fac.position
            )

    def test_bomb_resolve(self):
        source_fac = Factory(0, 1, 0, 0, (15, -10))
        dest_fac = Factory(1, 1, 0, 0, (-5, 20))

        unit = Bomb(None, source_fac, dest_fac)

        unit.travelled = factory_dist(source_fac, dest_fac)-1

        self.assertTrue(unit.active)

        unit.move()
        self.assertFalse(unit.active)
        self.assertEqual(source_fac.bombs_arriving, 0)
        self.assertEqual(dest_fac.bombs_arriving, 1)

    def test_troop_resolve(self):
        source_fac = Factory(-1, 1, 0, 0, (15, -10))
        dest_fac = Factory(1, 1, 0, 0, (-5, 20))

        unit = Troop(10, source_fac, dest_fac)

        unit.travelled = factory_dist(source_fac, dest_fac)-1

        self.assertTrue(unit.active)

        unit.move()
        self.assertFalse(unit.active)

        self.assertEqual(dest_fac.occupying_troops, {-1: 10, 1: 0})
