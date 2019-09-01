from abc import ABC, abstractmethod


class Jsonizable(ABC):
    """
    Class to serialize and deserialize game objects BETWEEN TURNS.
    No mid-turn data (e.g. orders, occupying troops, etc) should be relied on.
    """

    @abstractmethod
    def to_json(self):
        pass

    @classmethod
    @abstractmethod
    def from_json(cls, obj):
        pass


def json_encoder(obj):
    if isinstance(obj, Jsonizable):
        return obj._to_json()
    else:
        raise ValueError("Cannot encode an object that isn't Jsonizable")
