import numpy as np
import json
import unittest

from game import GameBoard
from jsonize import Jsonizable
from unit import Bomb, Troop


class TestClassA(Jsonizable):
    def __init__(self, attrib):
        self.attrib = attrib

    def to_json(self):
        return {
            "attrib": self.attrib,
        }

    @classmethod
    def from_json(cls, obj):
        return cls(obj["attrib"])


class TestClassB(Jsonizable):
    def __init__(self):
        self.list_of_a = []

    def to_json(self):
        return {
            "list_of_a": [a.to_json() for a in self.list_of_a],
        }

    @classmethod
    def from_json(cls, obj):
        b = cls()
        b.list_of_a = [TestClassA.from_json(a) for a in obj["list_of_a"]]
        return b


class TestJsonizeTestClasses(unittest.TestCase):
    def test_encode_simple(self):
        a = TestClassA(5)

        expected = {"attrib": 5}

        self.assertEqual(
            a.to_json(),
            expected,
        )

    def test_decode_simple(self):
        json = {"attrib": 5}

        a = TestClassA.from_json(json)
        self.assertIsInstance(a, TestClassA)
        self.assertEqual(a.attrib, 5)

    def test_valid_json_simple(self):
        a = TestClassA(5)

        jsoned = a.to_json()
        self.assertEqual(
            jsoned,
            json.loads(json.dumps(jsoned))
        )

    def test_encode_decode_complex(self):
        b = TestClassB()
        b.list_of_a = [
            TestClassA(6),
            TestClassA(None),
        ]

        expected = {
            "list_of_a": [{"attrib": 6}, {"attrib": None}]
        }

        jsoned = b.to_json()

        self.assertEqual(expected, jsoned)

        new_b = TestClassB.from_json(jsoned)
        self.assertIsInstance(new_b, TestClassB)
        self.assertEqual(
            [6, None],
            [a.attrib for a in new_b.list_of_a]
        )

        self.assertEqual(
            jsoned,
            json.loads(json.dumps(jsoned))
        )


class TestJsonizeGameObjects(unittest.TestCase):
    def test_game_serialize(self):
        # TODO: fully test
        test_game = GameBoard()
        test_game.init_game()

        troop_source = test_game.factories[0]
        troop_dest = test_game.factories[1]

        bomb_source = test_game.factories[2]
        bomb_dest = test_game.factories[3]

        test_game.troops.append(Troop(11, troop_source, troop_dest))
        test_game.bombs.append(Bomb(None, bomb_source, bomb_dest))

        jsonized = test_game.to_json()

        self.assertEqual(
            jsonized,
            json.loads(json.dumps(jsonized))
        )

        new_game = GameBoard.from_json(jsonized)

        np.testing.assert_allclose(
            [fac.position for fac in test_game.factories],
            [fac.position for fac in new_game.factories]
        )
