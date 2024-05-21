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

        # forces
        self.turnaround_strength = 2
        self.cohesion_strength = 0.01
        self.separation_strength = 2.0
        self.separation_distance = 30.0
        self.alignment_strength = 0.125
        self.alignment_distance = 50

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
        self.velocities += timestep * sum(
            force()
            for force in [self.turnaround_force, self.cohesion_force, self.separation_force, self.alignment_force]
        )

        # boid movement
        self.positions += timestep * self.velocities

    def turnaround_force(self):
        # boids should turnaround when moving out the designated area
        forces = []
        for pos in self.positions:
            force = [0, 0]
            if pos[0] < self.min_position[0]:
                force[0] = self.turnaround_strength
            if pos[0] > self.max_position[0]:
                force[0] = -self.turnaround_strength
            if pos[1] < self.min_position[1]:
                force[1] = self.turnaround_strength
            if pos[1] > self.max_position[1]:
                force[1] = -self.turnaround_strength
            forces.append(force)
        return np.array(forces)

    def cohesion_force(self):
        # boids attract each other
        return self.cohesion_strength * (self.positions.mean(axis=0)[np.newaxis] - self.positions)

    def separation_force(self):
        # boids avoid collisions
        displacements = self.positions[np.newaxis] - self.positions[:, np.newaxis]
        are_close = (displacements**2).sum(-1) ** 0.5 <= self.separation_distance
        return self.separation_strength * np.where(are_close[..., None], displacements, 0).sum(0)

    def alignment_force(self):
        # boids adapt their velocity to their nearby peers
        displacements = self.positions[np.newaxis] - self.positions[:, np.newaxis]
        velocity_differences = self.velocities[np.newaxis] - self.velocities[:, np.newaxis]
        are_close = (displacements**2).sum(-1) ** 0.5 <= self.alignment_distance
        return -self.alignment_strength * np.where(are_close[..., None], velocity_differences, 0).mean(0)

    def render(self, surface):
        for pos, velocity in zip(self.positions, self.velocities):
            angle = math.atan2(velocity[1], velocity[0])
            ax = math.cos(angle) * 30
            ay = math.sin(angle) * 30
            pygame.draw.circle(surface, "blue", pos, 10)
            pygame.draw.line(surface, "red", pos, pos + np.array([ax, ay]), 2)
