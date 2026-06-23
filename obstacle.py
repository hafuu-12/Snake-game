"""
obstacle.py

Handles the wall blocks that start appearing once you hit certain score
milestones. Wanted to make this gradually harder rather than dumping
a maze on the player at the start.
"""

import random
import pygame


class Obstacle:
    def __init__(self, milestone, blocks_per_milestone):
        self.blocks = []  # list of (x, y) tiles that act like walls
        self.milestone = milestone
        self.blocks_per_milestone = blocks_per_milestone
        self.last_milestone_reached = 0

    def reset(self):
        self.blocks = []
        self.last_milestone_reached = 0

    def maybe_add_blocks(self, score, cols, rows, blocked_cells):
        """Call this every time the score changes. Adds new wall blocks
        once the score crosses a new milestone."""
        current_milestone = score // self.milestone
        if current_milestone > self.last_milestone_reached:
            self.last_milestone_reached = current_milestone
            self._spawn_blocks(cols, rows, blocked_cells)

    def _spawn_blocks(self, cols, rows, blocked_cells):
        all_blocked = set(blocked_cells) | set(self.blocks)
        added = 0
        attempts = 0
        while added < self.blocks_per_milestone and attempts < 300:
            attempts += 1
            # keep obstacles away from the very edge, looks cleaner and
            # avoids accidentally boxing the snake in right at spawn
            x = random.randint(2, cols - 3)
            y = random.randint(2, rows - 3)
            if (x, y) not in all_blocked:
                self.blocks.append((x, y))
                all_blocked.add((x, y))
                added += 1

    def collides(self, pos):
        return pos in self.blocks

    def draw(self, surface, tile_size, offset_y=0):
        for bx, by in self.blocks:
            rect = pygame.Rect(bx * tile_size, by * tile_size + offset_y, tile_size, tile_size)
            pygame.draw.rect(surface, (80, 80, 90), rect)
            pygame.draw.rect(surface, (40, 40, 45), rect, width=2)
