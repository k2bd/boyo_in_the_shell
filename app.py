import math
import os
import random

import numpy as np
import pygame

from game import GameBoard
from unit import Bomb, Troop
from order import Move, Inc, SendBomb

PLAYER_ONE_PORT = 23833
PLAYER_TWO_PORT = 23834

FAC_TEXT_OFFSET = 10


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
        self.size = self.width, self.height = 640, 400
        self.center = np.array([self.width/2, self.height/2])
        # TODO: this should scale with game.max_dist
        self.scale = min(self.width, self.height) / 22.0

    def pygame_init(self):
        pygame.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        bgfile = os.path.join("res", "background.png")
        self._background = pygame.image.load(bgfile)

        self._running = True

        self.font = pygame.font.SysFont("arial", 12)
        self.load_sprites()

    def load_sprites(self):
        self.factory_sprites = {}

        for team, color in [(-1, "blue"), (0, "grey"), (1, "red")]:
            self.factory_sprites[team] = []
            for i in range(4):
                filename = "{}_fac_{}.png".format(color, i)
                path = os.path.join("res", filename)
                image = pygame.image.load(path).convert()

                self.factory_sprites[team].append(image)

        self.troop_sprites = {}
        self.bomb_sprites = {}

        for team, color in [(-1, "blue"), (1, "red")]:
            filename = "{}_troop.png".format(color)
            path = os.path.join("res", filename)
            image = pygame.image.load(path)

            self.troop_sprites[team] = image

            filename = "{}_bomb.png".format(color)
            path = os.path.join("res", filename)
            image = pygame.image.load(path)

            self.bomb_sprites[team] = image

    def on_event(self, event):
        pass

    def loop(self):
        # TODO: handle player input

        self.clock.tick()
        self.timer += self.clock.get_time()
        while self.timer > self.turn_time:
            self.timer -= self.turn_time

            # TODO: testing input
            for factory in self.game.factories:
                if factory.team in [-1, 1]:
                    self.game.orders[factory.team].append(
                        Inc(factory.id)
                    )
                    if factory.production == 3:
                        targets = self.game.factories.copy()
                        random.shuffle(targets)
                        if self.game.current_turn % 10 == 0:
                            self.game.orders[factory.team].append(
                                SendBomb(factory.id, targets[0].id)
                            )
                        for t_factory in targets:
                            if factory.id != t_factory.id:
                                self.game.orders[factory.team].append(
                                    Move(
                                        factory.id,
                                        t_factory.id,
                                        max(1, t_factory.stock),
                                    )
                                )
            # TODO: end testing input

            self.game.update()

        if self.game.game_over:
            self._running = False

    def render(self):
        # Clear screen
        self._display_surf.blit(self._background, (0, 0))

        for factory in self.game.factories:
            self.draw_factory(factory)

        for unit in self.game.troops + self.game.bombs:
            self.draw_unit(unit)

        pygame.display.flip()

    def draw(self, img, position, rotation=0.0):
        center = np.array(position) * self.scale + self.center
        topleft = (
            center[0] - img.get_width()/2,
            center[1] - img.get_height()/2
        )

        image = pygame.transform.rotate(img, rotation)

        self._display_surf.blit(image, topleft)

    def draw_factory(self, factory):
        team_facs = self.factory_sprites[factory.team]
        factory_sprite = team_facs[factory.production]

        self.draw(factory_sprite, factory.position)

        status = " (D)" if factory.disabled_turns > 0 else ""
        text = self.font.render(
            "{}{}".format(factory.stock, status),
            True,
            (255, 255, 255),
        )
        self.draw(text, factory.position)

    def draw_unit(self, unit):
        if type(unit) == Bomb:
            sprite = self.bomb_sprites[unit.team]
            status_text = ""
        elif type(unit) == Troop:
            sprite = self.troop_sprites[unit.team]
            status_text = str(unit.strength)
        else:
            raise ValueError("Unknown unit type {}".format(type(unit)))

        # Make the unit smoothly move to the destination
        draw_position = np.array(unit.get_position())

        direction = np.array(unit.destination.position) \
            - np.array(unit.source.position)

        # Timer in ms
        slide = direction * self.timer / (1000.0 * unit.distance)
        draw_position += slide

        rotation = math.degrees(math.atan2(direction[0], direction[1])) + 180

        self.draw(sprite, draw_position, rotation=rotation)

        text = self.font.render(
            status_text,
            True,
            (255, 255, 255),
        )
        self.draw(text, draw_position)

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
