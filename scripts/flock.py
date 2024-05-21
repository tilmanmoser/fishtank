import math
import numpy as np
import pygame


class Flock:
    def __init__(self, max=25, area=(0, 0, 0, 0)) -> None:
        self.max_boids = max
        self.min_position = np.array(area[:2])
        self.max_position = np.array(area[2:])

        self.min_velocity = np.array([0, -20])
        self.max_velocity = np.array([10, 20])

        self.positions = np.empty((0, 2), float)
        self.velocities = np.empty((0, 2), float)

    def add(self):
        if len(self.positions) >= self.max_boids:
            self.positions = np.delete(self.positions, 1, 0)
            self.velocities = np.delete(self.velocities, 1, 0)

        self.positions = np.append(
            self.positions,
            (
                self.min_position[:, np.newaxis]
                + np.random.rand(2, 1)
                * (self.max_position - self.min_position)[:, np.newaxis]
            ).reshape(1, 2),
            axis=0,
        )

        self.velocities = np.append(
            self.velocities,
            (
                self.min_velocity[:, np.newaxis]
                + np.random.rand(2, 1)
                * (self.max_velocity - self.min_velocity)[:, np.newaxis]
            ).reshape(1, 2),
            axis=0,
        )

    def update(self, timestep):
        self.positions += timestep * self.velocities

    def render(self, surface):
        for pos, velocity in zip(self.positions, self.velocities):
            angle = math.atan2(velocity[1], velocity[0])
            ax = math.cos(angle) * 30
            ay = math.sin(angle) * 30
            pygame.draw.circle(surface, "blue", pos, 10)
            pygame.draw.line(surface, "red", pos, pos + np.array([ax, ay]), 2)
