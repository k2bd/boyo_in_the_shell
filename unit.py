import numpy as np

from factory import factory_dist


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
