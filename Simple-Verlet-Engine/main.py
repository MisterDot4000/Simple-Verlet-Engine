import pygame as pg
import time
import math
import sys

from Scripts.node import Node
from Scripts.sticks import Stick
from Scripts.settings import *


class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((800, 750))
        self.clock = pg.time.Clock()
        self.FPS = 60
        self.font = pg.font.Font(None, 30)

        self.dt = 1 / self.FPS
        self.current_frame = time.time()
        self.last_frame = self.current_frame
        self.frame = 0

        self.gravity = gravity
        self.sub_steps = sub_steps
        self.radius = radius

        self.nodes = []
        self.sticks = []

        self.clicking = False
        self.right_clicking = False
        self.l_shifting = False
        self.pos = []
        self.size = [0, 0]
        self.tag = 0
        self.positions = []
        self.current_node = None

    @staticmethod
    def distance(p0, p1):
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]

        return math.sqrt(dx**2 + dy**2), (dx, dy)

    def update_dt(self):
        self.current_frame = time.time()
        self.dt = self.current_frame - self.last_frame
        self.last_frame = self.current_frame

    def add_box(self, size):
        self.tag += 1
        nodes = []
        sticks = []
        for pos in self.positions:
            nodes.append(Node(pos, self.radius, self, tag=self.tag, bounce=bounce))
        for i in range(len(nodes)):
            if len(nodes) > i + 1 and (i + 1) % size[1] != 0:
                sticks.append(Stick(nodes[i], nodes[i + 1], self.distance(nodes[i].pos_current, nodes[i + 1].pos_current)[0]))
            if len(nodes) > i + size[1]:
                sticks.append(Stick(nodes[i], nodes[i + size[1]], self.distance(nodes[i].pos_current, nodes[i + size[1]].pos_current)[0]))
            if len(nodes) > i + size[1] + 1 and (i + 1) % size[1] != 0:
                sticks.append(Stick(nodes[i], nodes[i + size[1] + 1], self.distance(nodes[i].pos_current, nodes[i + size[1] + 1].pos_current)[0]))

        for node in nodes:
            self.nodes.append(node)
        for stick in sticks:
            self.sticks.append(stick)

    def add_net(self, size):
        self.tag += 1
        nodes = []
        sticks = []
        first_row = set()
        for pos in range(len(self.positions)):
            if pos % size[1] == 0:
                first_row.add(self.positions[pos])
        for pos in self.positions:
            static = True if pos in first_row else False
            nodes.append(Node(pos, self.radius, self, tag=self.tag, static=static, bounce=bounce))
        for i in range(len(nodes)):
            if len(nodes) > i + 1 and (i + 1) % size[1] != 0:
                sticks.append(Stick(nodes[i], nodes[i + 1], self.distance(nodes[i].pos_current, nodes[i + 1].pos_current)[0]))
            if len(nodes) > i + size[1]:
                sticks.append(Stick(nodes[i], nodes[i + size[1]], self.distance(nodes[i].pos_current, nodes[i + size[1]].pos_current)[0]))

        for node in nodes:
            self.nodes.append(node)
        for stick in sticks:
            self.sticks.append(stick)

    def run(self):
        while True:
            self.clock.tick(self.FPS)
            self.frame += 1

            self.update_dt()

            pg.display.flip()
            self.screen.fill((100, 100, 100))
            if circle_constraint:
                pg.draw.circle(self.screen, (0, 0, 0), (400, 375), 375)  # draw circle constraint
            fps = self.font.render('FPS: ' + str(round(self.clock.get_fps(), 2)), None, 'black')
            objects = self.font.render('Objects: ' + str(len(self.nodes)), None, 'black')
            self.screen.blit(fps, (5, 5))
            self.screen.blit(objects, (5, 25))

            self.nodes.sort(key=lambda x: x.pos_current[0])
            dt = self.dt / self.sub_steps
            for i in range(self.sub_steps):
                for node in self.nodes:
                    node.update(dt)
                for node in self.nodes:
                    node.accelerate(self.gravity)
                for stick in self.sticks:
                    stick.update()
                if collide:
                    for node in self.nodes:
                        node.collisions()
                for node in self.nodes:
                    pos = (self.screen.get_width() // 2, self.screen.get_height() // 2) if circle_constraint else None
                    r = self.screen.get_height() // 2 if circle_constraint else None
                    node.constrain(pos=pos, radius=r)

            for stick in self.sticks:
                stick.render(self.screen)
            for node in self.nodes:
                node.render(self.screen)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        sys.exit()
                    if event.key == pg.K_LSHIFT:
                        self.l_shifting = True
                if event.type == pg.KEYUP:
                    if event.key == pg.K_LSHIFT:
                        self.l_shifting = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                    if event.button == 3:
                        self.right_clicking = True
                if event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                        self.current_node = None
                    if event.button == 3:
                        self.right_clicking = False
                        if self.l_shifting:
                            self.add_net(self.size)
                        else:
                            self.add_box(self.size)

            if self.clicking and not self.l_shifting:
                m_pos = pg.mouse.get_pos()
                if self.current_node:
                    dist = self.distance(self.current_node.pos_current, m_pos)
                    self.current_node.accelerate((dist[1][0] * dist[0], dist[1][1] * dist[0]))
                else:
                    for node in self.nodes:
                        if node.get_over(m_pos):
                            self.current_node = node
            elif self.l_shifting and self.clicking:
                if self.frame % 10 == 0:
                    self.nodes.append(Node((200, 200), self.radius, self, bounce=bounce))
                    self.nodes[-1].pos_old[0] -= 2
            else:
                self.current_node = None

            if self.right_clicking:
                self.positions = []
                m_pos = pg.mouse.get_pos()
                if not self.pos:
                    self.pos = m_pos
                self.size = self.distance(self.pos, m_pos)[1]
                space = 4 if self.l_shifting else 2
                self.size = [int(self.size[0] // (self.radius * space)), int(self.size[1] // (self.radius * space))]
                for pos_x in range(self.size[0]):
                    pos_x *= self.radius * space
                    pos_x += self.pos[0] + self.radius
                    for pos_y in range(self.size[1]):
                        pos_y *= self.radius * space
                        pos_y += self.pos[1] + self.radius
                        pg.draw.circle(self.screen, (255, 255, 255), (pos_x, pos_y), self.radius)
                        self.positions.append((pos_x, pos_y))
            else:
                self.pos = []


App().run()
