import pygame as pg
import math
pg.init()


class Node:
    def __init__(self, pos, radius, app, bounce=True, static=False, tag=None):
        self.pos_current = list(pos)
        self.pos_old = list(pos)
        self.acc = [0, 0]
        self.radius = radius
        self.vel = [0, 0]
        self.app = app
        self.bounce = bounce
        self.color = (255, 255, 255)

        self.static = static
        self.tag = tag

    def get_over(self, pos):
        if self.pos_current[0] - self.radius <= pos[0] <= self.pos_current[0] + self.radius:
            if self.pos_current[1] - self.radius <= pos[1] <= self.pos_current[1] + self.radius:
                return True
        return False

    def update(self, dt):
        if not self.static:
            self.vel = [self.pos_current[0] - self.pos_old[0], self.pos_current[1] - self.pos_old[1]]

            self.pos_old = self.pos_current.copy()
            self.pos_current[0] += self.vel[0] + self.acc[0] * dt * dt
            self.pos_current[1] += self.vel[1] + self.acc[1] * dt * dt

            self.acc = [0, 0]

    def accelerate(self, acc):
        self.acc[0] += acc[0]
        self.acc[1] += acc[1]

    def collisions(self):
        for node in self.app.nodes:
            too_much_on_left = node.pos_current[0] + node.radius <= self.pos_current[0] - self.radius
            same_tag = True if self.tag == node.tag and self.tag is not None else False
            if too_much_on_left or node == self or same_tag:
                continue
            if self.pos_current[0] + self.radius < node.pos_current[0] - node.radius:
                return True
            collision_axis = [self.pos_current[0] - node.pos_current[0], self.pos_current[1] - node.pos_current[1]]
            dist = math.sqrt(collision_axis[0] ** 2 + collision_axis[1] ** 2)

            min_dist = self.radius + node.radius
            if dist < min_dist:
                n = (collision_axis[0] / dist, collision_axis[1] / dist)
                delta = min_dist - dist
                self.pos_current[0] += 0.5 * delta * n[0]
                self.pos_current[1] += 0.5 * delta * n[1]
                node.pos_current[0] -= 0.5 * delta * n[0]
                node.pos_current[1] -= 0.5 * delta * n[1]

    def circle_constraint(self, pos, radius):
        vec_dist = [self.pos_current[0] - pos[0], self.pos_current[1] - pos[1]]
        dist = math.sqrt(vec_dist[0] ** 2 + vec_dist[1] ** 2)

        if dist > radius - self.radius:
            n = (vec_dist[0] / dist, vec_dist[1] / dist)
            self.pos_current = [pos[0] + n[0] * (radius - self.radius), pos[1] + n[1] * (radius - self.radius)]

    def screen_constrain(self):
        if self.bounce:
            if self.pos_current[0] + self.radius >= self.app.screen.get_width():
                t = (self.app.screen.get_width() - self.radius - self.pos_old[0]) / (self.pos_current[0] - self.pos_old[0])
                vec_dist = (self.pos_current[0] - self.pos_old[0], self.pos_current[1] - self.pos_old[1])

                self.pos_current = [self.app.screen.get_width() - self.radius, self.pos_current[1] * t + self.pos_old[1] * (1 - t)]
                self.pos_old = [self.pos_current[0] + vec_dist[0], self.pos_current[1] - vec_dist[1]]
            if self.pos_current[1] + self.radius >= self.app.screen.get_height():
                t = (self.app.screen.get_height() - self.radius - self.pos_old[1]) / (self.pos_current[1] - self.pos_old[1])
                vec_dist = (self.pos_current[0] - self.pos_old[0], self.pos_current[1] - self.pos_old[1])

                self.pos_current = [self.pos_current[0] * t + self.pos_old[0] * (1 - t), self.app.screen.get_height() - self.radius]
                self.pos_old = [self.pos_current[0] - vec_dist[0], self.pos_current[1] + vec_dist[1]]
            if self.pos_current[0] - self.radius <= 0:
                t = (self.radius - self.pos_old[0]) / (self.pos_current[0] - self.pos_old[0])
                vec_dist = (self.pos_current[0] - self.pos_old[0], self.pos_current[1] - self.pos_old[1])

                self.pos_current = [self.radius, self.pos_current[1] * t + self.pos_old[1] * (1 - t)]
                self.pos_old = [self.pos_current[0] + vec_dist[0], self.pos_current[1] - vec_dist[1]]
            if self.pos_current[1] - self.radius <= 0:
                t = (self.radius - self.pos_old[1]) / (self.pos_current[1] - self.pos_old[1])
                vec_dist = (self.pos_current[0] - self.pos_old[0], self.pos_current[1] - self.pos_old[1])

                self.pos_current = [self.pos_current[0] * t + self.pos_old[0] * (1 - t), self.radius]
                self.pos_old = [self.pos_current[0] - vec_dist[0], self.pos_current[1] + vec_dist[1]]
        else:
            if self.pos_current[0] + self.radius > self.app.screen.get_width():
                self.pos_current[0] = self.app.screen.get_width() - self.radius
            if self.pos_current[1] + self.radius >= self.app.screen.get_height():
                self.pos_current[1] = self.app.screen.get_height() - self.radius
            if self.pos_current[0] - self.radius <= 0:
                self.pos_current[0] = self.radius
            if self.pos_current[1] - self.radius <= 0:
                self.pos_current[1] = self.radius

    def constrain(self, pos=None, radius=None):
        if not self.static:
            self.circle_constraint(pos, radius) if pos and radius else self.screen_constrain()

    def render(self, surf):
        pg.draw.circle(surf, self.color, self.pos_current, self.radius)

