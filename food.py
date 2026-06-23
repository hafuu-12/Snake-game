"""
food.py

Regular food the snake eats to grow + score a point, and a special
"bonus food" that only shows up sometimes, is worth more points, and
disappears again if you don't grab it fast enough.
"""

import random
import pygame


class Food:
    def __init__(self, cols, rows, tile_size):
        self.tile_size = tile_size
        self.cols = cols
        self.rows = rows
        self.pos = (0, 0)
        self.color = (210, 45, 45)

    def respawn(self, blocked_cells):
        """blocked_cells should be a set/list of (x,y) we can't spawn on."""
        # there's technically a chance this loops forever on a near-full
        # board but realistically the snake would fill the whole screen
        # before that happens so not worrying about it
        while True:
            pos = (random.randint(0, self.cols - 1), random.randint(0, self.rows - 1))
            if pos not in blocked_cells:
                self.pos = pos
                return

    def draw(self, surface, offset_y=0):
        rect = pygame.Rect(
            self.pos[0] * self.tile_size,
            self.pos[1] * self.tile_size + offset_y,
            self.tile_size,
            self.tile_size,
        )
        pygame.draw.rect(surface, self.color, rect, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), rect, width=1, border_radius=8)


class BonusFood:
    """
    Shows up randomly, worth extra points, but only sticks around for a
    few seconds. Kept separate from Food instead of subclassing it because
    the timing/blinking logic didn't really share much with the base class
    and inheritance was making it more confusing, not less.
    """

    def __init__(self, tile_size, lifetime_ms, points):
        self.tile_size = tile_size
        self.lifetime = lifetime_ms
        self.points = points
        self.active = False
        self.pos = None
        self.spawn_time = 0
        self.color = (255, 200, 0)

    def spawn(self, cols, rows, blocked_cells):
        for _ in range(200):  # give up after enough tries instead of risking an infinite loop
            pos = (random.randint(0, cols - 1), random.randint(0, rows - 1))
            if pos not in blocked_cells:
                self.pos = pos
                self.active = True
                self.spawn_time = pygame.time.get_ticks()
                return

    def update(self):
        if self.active and pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.active = False

    def time_left_ratio(self):
        if not self.active:
            return 0
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0, 1 - elapsed / self.lifetime)

    def draw(self, surface, offset_y=0):
        if not self.active:
            return
        # blink faster as it's about to expire - gives a visual warning
        ratio = self.time_left_ratio()
        blink_speed = 150 if ratio > 0.3 else 60
        if (pygame.time.get_ticks() // blink_speed) % 2 == 0:
            rect = pygame.Rect(
                self.pos[0] * self.tile_size,
                self.pos[1] * self.tile_size + offset_y,
                self.tile_size,
                self.tile_size,
            )
            pygame.draw.rect(surface, self.color, rect, border_radius=10)
            pygame.draw.rect(surface, (130, 90, 0), rect, width=2, border_radius=10)
