from abc import ABC, abstractmethod

import numpy as np

from factory import factory_dist


class Unit(ABC):
    def __init__(self, strength, source, destination):
        self.strength = strength

        self.active = True

        # N.B. implement a jsonize that just outputs source, dest IDs
        self.source = source
        self.destination = destination

        self.team = self.source.team

        self.distance = factory_dist(source, destination)
        self.travelled = 0

    @abstractmethod
    def resolve_at_dest(self):
        pass

    def move(self):
        self.travelled += 1
        if self.travelled == self.distance:
            self.resolve_at_dest()
            self.active = False

    def get_position(self):
        vec = np.array(self.destination.position, dtype="float64") \
            - np.array(self.source.position, dtype="float64")

        vec *= self.travelled / self.distance

        return self.source.position + vec


class Troop(Unit):
    def resolve_at_dest(self):
        self.destination.occupying_troops[self.team] += self.strength


class Bomb(Unit):
    def resolve_at_dest(self):
        self.destination.bombs_arriving += 1
