import unittest

from unit import Unit, Bomb, Troop


class TestUnits(unittest.TestCase):
    def setUp(self):
        self.unit_types = [Bomb, Troop]

    def test_cannot_init_base_unit(self):
        with self.assertRaises(TypeError) as err:
            Unit(1, None, None)

        self.assertIn(
            "Can't instantiate abstract",
            str(err.exception)
        )
