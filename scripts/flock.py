import math
import os
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
        self.separation_strength = 2.0
        self.separation_distance = 50.0
        self.alignment_strength = 0.125
        self.alignment_distance = 50
        self.flee_strength = 1.0
        self.flee_distance = 150.0
        self.attraction_distance = 200.0
        self.attraction_strength = 2.0

        # boids
        self.boids = []
        self.positions = np.empty((0, 2), float)
        self.velocities = np.empty((0, 2), float)

        # predator
        self.predator = np.array(self.max_position, float)
        self.predator_speed = 50
        self.predator_images = self.load_images(os.path.join("data/images/submarine"))
        self.predator_frame = 0
        self.predator_flip = True

        # food
        self.food_surface = pygame.Surface((10, 10))
        self.food_surface.set_colorkey((0, 0, 0, 0))
        pygame.draw.circle(self.food_surface, "brown", (5, 5), 5)
        self.food = []
        self.food_speed = 20
        self.food_collision_distance = 20

        # debug
        self.font = pygame.font.Font(pygame.font.get_default_font(), 20)

    def add(self, image):
        if len(self.boids) >= self.max_boids:
            # remove first(=oldest) element from array
            self.boids.pop(0)
            self.positions = np.delete(self.positions, 0, 0)
            self.velocities = np.delete(self.velocities, 0, 0)

        # append new boid
        self.boids.append(image)
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
        self.update_predator(timestep, predator_movement)
        self.update_food(timestep)
        self.update_boids(timestep)

    def update_boids(self, timestep):
        # apply forces
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

        # restrict to min/max velocity
        self.velocities = np.clip(self.velocities, self.min_velocity, self.max_velocity)

        # move boids
        self.positions += timestep * self.velocities

    def update_food(self, timestep):
        for item in self.food.copy():
            item[1] += timestep * self.food_speed
            item[0] += math.cos(item[1] / math.pi) / 100 * self.food_speed
            if item[1] > self.max_position[1]:
                self.food.remove(item)
                continue
            for pos in self.positions:
                if (
                    abs(pos[0] - item[0]) < self.food_collision_distance
                    and abs(pos[1] - item[1]) < self.food_collision_distance
                    and item in self.food
                ):
                    self.food.remove(item)

    def update_predator(self, timestep, predator_movement):
        # predator movement
        self.predator += timestep * np.array(predator_movement) * self.predator_speed
        self.predator = np.clip(self.predator, self.min_position, self.max_position)

        # flip
        if predator_movement[0] < 0:
            self.predator_flip = True
        elif predator_movement[0] > 0:
            self.predator_flip = False

        # update animation frame
        self.predator_frame = (self.predator_frame + 1) % len(self.predator_images)

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
            displacements = self.positions[np.newaxis] - np.array(self.food)[:, np.newaxis]
            are_close = (displacements**2).sum(-1) ** 0.5 <= self.attraction_distance
            return -self.attraction_strength * np.where(are_close[..., None], displacements, 0).sum(0)
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

    def load_images(self, path):
        images = []
        for file in sorted(os.listdir(path)):
            if file.endswith(".png"):
                images.append(pygame.image.load(os.path.join(path, file)).convert_alpha())
        return images

    def render(self, surface):
        # predator
        predator_image = self.predator_images[self.predator_frame]
        surface.blit(
            pygame.transform.flip(predator_image, self.predator_flip, False),
            (self.predator[0] - predator_image.get_width() / 2, self.predator[1] - predator_image.get_height() / 2),
        )

        # food
        for pos in self.food:
            surface.blit(
                self.food_surface,
                (pos[0] - self.food_surface.get_width() / 2, pos[1] - self.food_surface.get_height() / 2),
            )

        # boids
        for boid, pos, velocity in zip(self.boids, self.positions, self.velocities):
            angle = (math.atan2(-velocity[1], velocity[0]) / math.pi * 180) % 360
            if angle < 0:
                angle += 360
            img = pygame.transform.rotate(pygame.transform.flip(boid.copy(), False, velocity[0] < 0), angle)
            surface.blit(img, (pos[0] - img.get_width() // 2, pos[1] - img.get_height() // 2))
