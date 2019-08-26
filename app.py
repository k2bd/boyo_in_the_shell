import os

import numpy as np
import pygame

from game import GameBoard
from unit import Bomb, Troop

PLAYER_ONE_PORT = 23833
PLAYER_TWO_PORT = 23834


class App:
    def __init__(self, turn_time=1000.0):
        """
        Parameters
        ----------
        turn_time : float
            Time for one turn [ms]
        """

        self.turn_time = turn_time
        self.game = GameBoard()
        self.game.init_game()

        self.timer = 0.0

        # Game timer
        self.size = self.weight, self.height = 640, 400

    def pygame_init(self):
        pygame.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._background = pygame.Surface(self._display_surf.get_size())
        self._background.fill((0, 0, 0))

        self._running = True

        self.font = pygame.font.SysFont("arial", 16)
        self.load_sprites()

    def load_sprites(self):
        self.factory_sprites = {}

        for team, color in [(-1, "blue"), (0, "grey"), (1, "red")]:
            self.factory_sprites[team] = []
            for i in range(4):
                b = pygame.sprite.Sprite()
                filename = "{}_fac_{}.png".format(color, i)
                path = os.path.join("res", filename)
                b.image = pygame.image.load(path).convert()
                b.rect = b.image.get_rect()

                self.factory_sprites[team].append(b)

        self.troop_sprites = {}
        self.bomb_sprites = {}

        for team, color in [(-1, "blue"), (1, "red")]:
            b = pygame.sprite.Sprite()
            filename = "{}_troop.png".format(color)
            path = os.path.join("res", filename)
            b.image = pygame.image.load(path).convert()
            b.rect = b.image.get_rect()

            self.troop_sprites[team] = b

            b = pygame.sprite.Sprite()
            filename = "{}_bomb.png".format(color)
            path = os.path.join("res", filename)
            b.image = pygame.image.load(path).convert()
            b.rect = b.image.get_rect()

            self.bomb_sprites[team] = b

    def on_event(self, event):
        pass

    def loop(self):
        # TODO: handle player input

        self.clock.tick()
        self.timer += self.clock.get_time()
        while self.timer > self.turn_time:
            self.timer -= self.turn_time
            self.game.update()

    def render(self):
        # Clear screen
        self._display_surf.blit(self._background, (0, 0))

        for factory in self.game.factories:
            self.draw_factory(factory)

        for unit in self.game.troops + self.game.bombs:
            self.draw_unit(unit)

    def draw_factory(self, factory):
        print("Drawing factory")
        team_facs = self.factory_sprites[factory.team]
        factory_sprite = team_facs[factory.production]

        factory_sprite.center = factory.position

        self._display_surf.blit(factory_sprite)

    def draw_unit(self, unit):
        if type(unit) == Bomb:
            sprite = self.bomb_sprites[unit.team]
        elif type(unit) == Troop:
            sprite = self.troop_sprites[unit.team]
        else:
            raise ValueError("Unknown unit type {}".format(type(unit)))

        # Make the unit smoothly move to the destination
        draw_position = np.array(unit.position)
        slide = np.array(unit.destination) - np.array(unit.source)
        slide *= self.timer / (1000.0 * unit.distance)  # Timer in ms
        draw_position += slide

        sprite.center = draw_position.tolist()

        self._display_surf.blit(sprite)

    def cleanup(self):
        self.font = None
        pygame.font.quit()
        pygame.quit()

    def execute(self):
        if self.pygame_init() is False:
            self._running = False

        self.render()
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.loop()
            self.render()
        self.cleanup()


if __name__ == "__main__":
    my_app = App()
    my_app.execute()
