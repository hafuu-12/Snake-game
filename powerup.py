"""
powerup.py

Power-ups that occasionally spawn on the board:
  - slow  : temporarily slows the snake down
  - double: temporarily doubles points earned from food
  - shield: blocks the next collision (used once, then gone)

The actual EFFECT of each power-up is applied in game.py since that's
where score/speed/shield state already lives - this class just handles
spawning it on the board and knowing what kind it is.
"""

import random
import pygame
from settings import POWERUP_LIFETIME_ON_BOARD


class PowerUp:
    KINDS = ["slow", "double", "shield"]

    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.active = False
        self.pos = None
        self.kind = None
        self.spawn_time = 0

        # random-ish cooldown between spawns so they don't show up constantly
        self.next_spawn_delay = random.randint(9000, 16000)
        self.last_spawn_attempt = pygame.time.get_ticks()

    def update(self, cols, rows, blocked_cells):
        now = pygame.time.get_ticks()

        if self.active:
            if now - self.spawn_time > POWERUP_LIFETIME_ON_BOARD:
                self.active = False
                self.last_spawn_attempt = now
                self.next_spawn_delay = random.randint(10000, 18000)
            return

        if now - self.last_spawn_attempt > self.next_spawn_delay:
            self._try_spawn(cols, rows, blocked_cells, now)

    def _try_spawn(self, cols, rows, blocked_cells, now):
        for _ in range(150):
            pos = (random.randint(0, cols - 1), random.randint(0, rows - 1))
            if pos not in blocked_cells:
                self.pos = pos
                self.kind = random.choice(self.KINDS)
                self.active = True
                self.spawn_time = now
                return

    def draw(self, surface, offset_y=0):
        if not self.active:
            return
        from settings import POWERUP_COLORS
        color = POWERUP_COLORS.get(self.kind, (255, 255, 255))
        cx = self.pos[0] * self.tile_size + self.tile_size // 2
        cy = self.pos[1] * self.tile_size + self.tile_size // 2 + offset_y
        radius = self.tile_size // 2 - 2

        # pulse the size a bit so it stands out from regular food
        pulse = int(2 * abs((pygame.time.get_ticks() % 600) - 300) / 300)
        pygame.draw.circle(surface, color, (cx, cy), radius + pulse)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), radius + pulse, width=2)

        # little letter in the middle as a hint (S, D, or letter for shield)
        letter = {"slow": "S", "double": "D", "shield": "P"}.get(self.kind, "?")
        font = pygame.font.SysFont(None, self.tile_size)
        txt = font.render(letter, True, (20, 20, 20))
        surface.blit(txt, txt.get_rect(center=(cx, cy)))
