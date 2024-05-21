import os
import re
import time
import cv2
import pygame

from watchdog.observers import Observer
from scripts.flock import Flock
from scripts.scanner import Scanner
from scripts.imageFileEventHandler import ImageFileEventHandler

FPS = 25  # adjust to video FPS


class Aquarium:
    def __init__(self) -> None:
        # display
        pygame.init()
        pygame.display.set_caption("Flock")
        self.scale = 1
        self.margin = [0, 0]
        self.display = pygame.Surface((1280, 720))
        self.screen = pygame.display.set_mode(self.display.get_size(), pygame.RESIZABLE)
        self.on_resize()

        # background video & audio
        self.video = cv2.VideoCapture(os.path.join("data/video/underwater.mp4"))
        self.audio = pygame.mixer.Sound(os.path.join("data/audio/aquarium-ambience.mp3"))
        self.muted = True

        # objects
        self.movement = [False, False, False, False]
        self.flock = Flock(max=25, area=(100, 100, self.display.get_width() - 100, self.display.get_height() - 100))
        self.load_boids()

        # ticks / fps
        self.clock = pygame.Clock()

        # hide mouse
        pygame.mouse.set_visible(False)

    def load_boids(self):
        path = os.path.join("data/outbound")
        # load 25 boids reverse sorted by date, but in sorted order, so that the oldest is at index 0
        for file in sorted(sorted(os.listdir(path), reverse=True)[:25]):
            self.load_boid(os.path.join(path, file))

    def load_boid(self, file):
        match = re.search("^.*[0-9]{20}-([0-9]{1}).png", file)
        if match:
            # load image
            img = pygame.image.load(os.path.join(file)).convert_alpha()
            # scale down
            img = pygame.transform.smoothscale(img, (100, 142))
            # make them look "right" (which is 0 degree angle in pygame)
            img = pygame.transform.flip(pygame.transform.rotate(img, -90), False, True)
            # add fish to flock, match.group(1) == type of fisch from filename
            self.flock.add(img)

    def on_resize(self):
        self.scale = min(
            self.screen.get_width() / self.display.get_width(), self.screen.get_height() / self.display.get_height()
        )
        self.margin[0] = int((self.screen.get_width() - self.display.get_width() * self.scale) // 2)
        self.margin[1] = int((self.screen.get_height() - self.display.get_height() * self.scale) // 2)

    def update(self):
        self.flock.update(
            self.clock.get_time() / 1000, (self.movement[1] - self.movement[0], self.movement[3] - self.movement[2])
        )

    def render(self):
        self.display.fill((0, 0, 0, 0))
        self.display.blit(self.get_video_frame(), (0, 0))
        self.flock.render(self.display)

        self.screen.fill((0, 0, 0, 0))
        self.screen.blit(pygame.transform.smoothscale_by(self.display, self.scale), self.margin)
        pygame.display.flip()

    def get_video_frame(self):
        if not self.video.isOpened():
            return pygame.Surface(self.display.get_size())
        success, frame = self.video.read()
        if success:
            surface = pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "BGR")
            return surface
        else:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return self.get_video_frame()

    def toggle_audio(self):
        self.muted = not self.muted
        if self.muted:
            self.audio.stop()
        else:
            self.audio.set_volume(0.25)
            self.audio.play(-1)

    def run(self):
        # file observer for adding boids
        observer = Observer()
        image_event_handler = ImageFileEventHandler(
            Scanner(), os.path.join("data", "outbound"), remove=True, callback=self.load_boid
        )
        observer.schedule(image_event_handler, os.path.join("data", "inbound"), recursive=True)
        observer.start()

        # audio
        self.toggle_audio()

        # main loop
        try:
            running = True
            while running:

                self.update()
                self.render()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type in (pygame.VIDEOEXPOSE, pygame.VIDEORESIZE):
                        self.on_resize()
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
                        if event.key == pygame.K_m:
                            self.toggle_audio()
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
        finally:
            # clean up
            observer.stop()
            observer.join()
            self.video.release()
            pygame.quit()
