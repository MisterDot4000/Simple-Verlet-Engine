import pygame as pg
import math
pg.init()


class Stick:
    def __init__(self, node1, node2, length):
        self.node1 = node1
        self.node2 = node2
        self.length = length

    def update(self):
        dx = self.node2.pos_current[0] - self.node1.pos_current[0]
        dy = self.node2.pos_current[1] - self.node1.pos_current[1]
        dist = math.sqrt(dx**2 + dy**2)
        diff = self.length - dist
        percent = (diff / dist) / 2

        offset_x = dx * percent
        offset_y = dy * percent

        if not self.node1.static:
            self.node1.pos_current[0] -= offset_x
            self.node1.pos_current[1] -= offset_y

        if not self.node2.static:
            self.node2.pos_current[0] += offset_x
            self.node2.pos_current[1] += offset_y

    def render(self, surf):
        pg.draw.line(surf, (255, 255, 255), self.node1.pos_current, self.node2.pos_current)
