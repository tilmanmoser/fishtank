import pygame

from scripts.flock import Flock

FPS = 60


class Aquarium:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Flock")
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.Clock()

        self.flock = Flock(max=25, area=(100, 100, self.screen.get_width() - 100, self.screen.get_height() - 100))
        for i in range(50):
            self.flock.add()

        self.movement = [False, False, False, False]

    def update(self):
        self.flock.update(
            self.clock.get_time() / 1000, (self.movement[1] - self.movement[0], self.movement[3] - self.movement[2])
        )

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
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.movement[0] = True
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.movement[1] = True
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.movement[2] = True
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.movement[3] = True
                    if event.key == pygame.K_f:
                        self.flock.feed()
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.movement[0] = False
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.movement[1] = False
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.movement[2] = False
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.movement[3] = False

            self.clock.tick(FPS)

        pygame.quit()
