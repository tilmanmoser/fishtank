import pygame

from scripts.flock import Flock

FPS = 60


class Aquarium:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Flock")
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.Clock()
        self.flock = Flock(max=50, area=(50, 50, self.screen.get_width() - 50, self.screen.get_height() - 50))
        for i in range(50):
            self.flock.add()

    def update(self):
        self.flock.update(self.clock.get_time() / 1000)

    def render(self):
        self.screen.fill((0, 0, 0, 0))
        self.flock.render(self.screen)
        pygame.display.flip()

    def run(self):
        running = True
        while running:

            self.update()
            self.render()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.clock.tick(FPS)

        pygame.quit()
