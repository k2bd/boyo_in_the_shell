import pygame


class App:
    def __init__(self):
        pass

    def pygame_init(self):
        pygame.init()
        pygame.font.init()

        self._running = True

        self.font = pygame.font.SysFont("arial", 16)

    def on_event(self, event):
        pass

    def loop(self):
        pass

    def render(self):
        # Clear screen
        self._display_surf.blit(self._background, (0, 0))

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
