import math
import random
import numpy as np
import pygame


class Flock:
    def __init__(
        self,
        max=25,
        area=(0, 0, 0, 0),
    ) -> None:
        # limits
        self.max_boids = max
        self.min_position = np.array(area[:2])
        self.max_position = np.array(area[2:])
        self.min_velocity = np.array([-40, -40])
        self.max_velocity = np.array([40, 40])

        # forces
        self.turnaround_strength = 20
        self.cohesion_strength = 0.01
        self.separation_strength = 1.0
        self.separation_distance = 30.0
        self.alignment_strength = 0.125
        self.alignment_distance = 50
        self.flee_strength = 1.0
        self.flee_distance = 150.0
        self.attraction_strength = 0.1

        # boids
        self.positions = np.empty((0, 2), float)
        self.velocities = np.empty((0, 2), float)

        # predator
        self.predator = np.array(self.max_position, float)
        self.predator_speed = 50
        self.predator_flip = True

        # food
        self.food = []
        self.food_speed = 20

        # debug
        self.font = pygame.font.Font(pygame.font.get_default_font(), 20)

    def add(self):
        if len(self.positions) >= self.max_boids:
            # remove first(=oldest) element from array
            self.positions = np.delete(self.positions, 0, 0)
            self.velocities = np.delete(self.velocities, 0, 0)

        # append new boid
        self.positions = np.append(self.positions, self.random2d(self.min_position, self.max_position), axis=0)
        self.velocities = np.append(self.velocities, self.random2d(self.min_velocity, self.max_velocity), axis=0)

    def feed(self):
        item = [random.randint(self.min_position[0], self.max_position[0]), 0]
        self.food.append(item)

    def random2d(self, lower_limits=np.array([0, 0]), upper_limits=np.array([0, 0])):
        range = upper_limits - lower_limits
        rand = lower_limits[:, np.newaxis] + np.random.rand(2, 1) * range[:, np.newaxis]
        rand = rand.reshape(1, 2)
        return rand

    def update(self, timestep, predator_movement):
        self.predator += timestep * np.array(predator_movement) * self.predator_speed
        self.predator = np.clip(self.predator, self.min_position, self.max_position)

        for item in self.food.copy():
            item[1] += timestep * self.food_speed
            item[0] += math.cos(item[1] / math.pi) / 100 * self.food_speed
            if item[1] > self.max_position[1]:
                self.food.remove(item)

        self.velocities += timestep * sum(
            force()
            for force in [
                self.cohesion_force,
                self.separation_force,
                self.alignment_force,
                self.attraction_force,
                self.flee_force,
                self.turnaround_force,
            ]
        )
        self.velocities = np.clip(self.velocities, self.min_velocity, self.max_velocity)

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

    def flee_force(self):
        # boids flee from predator
        displacements = self.positions[np.newaxis] - self.predator
        are_close = (displacements**2).sum(-1) ** 0.5 <= self.flee_distance
        return self.flee_strength * np.where(are_close[..., None], displacements, 0).sum(0)

    def attraction_force(self):
        if len(self.food):
            # boids are attracted by food
            return self.attraction_strength * (
                np.array(self.food).reshape(len(self.food), 2).mean(axis=0)[np.newaxis] - self.positions
            )
        return np.empty(shape=(len(self.positions), 2))

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
        # predator
        pygame.draw.circle(surface, "green", self.predator, 10)

        # food
        for pos in self.food:
            pygame.draw.circle(surface, "brown", pos, 5)

        # boids
        for pos, velocity in zip(self.positions, self.velocities):
            angle = math.atan2(velocity[1], velocity[0])
            ax = math.cos(angle) * 30
            ay = math.sin(angle) * 30
            pygame.draw.circle(surface, "blue", pos, 10)
            pygame.draw.line(surface, "red", pos, pos + np.array([ax, ay]), 2)
            surface.blit(self.font.render(f"{int(velocity[0])},{int(velocity[1])}", True, "white"), pos)
