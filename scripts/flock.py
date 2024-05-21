import math
import numpy as np
import pygame


class Flock:
    def __init__(self, max=25, area=(0, 0, 0, 0)) -> None:
        # limits
        self.max_boids = max
        self.min_position = np.array(area[:2])
        self.max_position = np.array(area[2:])
        self.min_velocity = np.array([0, -20])
        self.max_velocity = np.array([10, 20])

        # boids
        self.positions = np.empty((0, 2), float)
        self.velocities = np.empty((0, 2), float)

    def add(self):
        if len(self.positions) >= self.max_boids:
            # remove first(=oldest) element from array
            self.positions = np.delete(self.positions, 1, 0)
            self.velocities = np.delete(self.velocities, 1, 0)

        # append new boid
        self.positions = np.append(self.positions, self.random2d(self.min_position, self.max_position), axis=0)
        self.velocities = np.append(self.velocities, self.random2d(self.min_velocity, self.max_velocity), axis=0)

    def random2d(self, lower_limits=np.array([0, 0]), upper_limits=np.array([0, 0])):
        range = upper_limits - lower_limits
        rand = lower_limits[:, np.newaxis] + np.random.rand(2, 1) * range[:, np.newaxis]
        rand = rand.reshape(1, 2)
        return rand

    def update(self, timestep):
        # boid movement
        self.positions += timestep * self.velocities

    def render(self, surface):
        for pos, velocity in zip(self.positions, self.velocities):
            angle = math.atan2(velocity[1], velocity[0])
            ax = math.cos(angle) * 30
            ay = math.sin(angle) * 30
            pygame.draw.circle(surface, "blue", pos, 10)
            pygame.draw.line(surface, "red", pos, pos + np.array([ax, ay]), 2)
