"""
snake.py

The Snake class itself. Body is just a list of (x, y) grid coordinates,
index 0 is always the head. Movement works by sticking a new head on
the front and popping the tail off the back, unless we're supposed to
be growing that turn.
"""

import pygame


class Snake:
    def __init__(self, start_x, start_y, theme):
        # start with 3 segments facing right so it doesn't look like a
        # single dot when the game begins
        self.body = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y),
        ]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow_pending = 0

        self.head_color, self.body_color = theme

        # shield power up - True means the next collision gets ignored
        # instead of ending the game
        self.shield_active = False

    def set_theme(self, theme):
        self.head_color, self.body_color = theme

    def change_direction(self, new_dir):
        """
        Queue up a direction change. We don't apply it immediately because
        if you press two keys in the same frame (happens more than you'd
        think with keyboard input) the snake could reverse into itself.
        """
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir == opposite:
            return  # ignore, can't go backwards into your own body
        self.next_direction = new_dir

    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        self.grow_pending += amount

    def get_head(self):
        return self.body[0]

    def occupies(self, pos):
        return pos in self.body

    def check_self_collision(self):
        head = self.body[0]
        # head touching any OTHER segment counts as a crash
        return head in self.body[1:]

    def check_wall_collision(self, cols, rows):
        x, y = self.body[0]
        return x < 0 or x >= cols or y < 0 or y >= rows

    def draw(self, surface, tile_size, offset_y=0):
        for i, segment in enumerate(self.body):
            x = segment[0] * tile_size
            y = segment[1] * tile_size + offset_y
            rect = pygame.Rect(x, y, tile_size, tile_size)

            if i == 0:
                color = self.head_color
            else:
                color = self.body_color

            pygame.draw.rect(surface, color, rect, border_radius=6)

            # little eyes on the head so you can tell which way it's facing,
            # purely cosmetic but it makes a surprising difference visually
            if i == 0:
                eye_size = max(2, tile_size // 7)
                dx, dy = self.direction
                cx, cy = rect.center
                offset = tile_size // 4
                eye1 = (cx - dy * offset + dx * offset // 2, cy - dx * offset + dy * offset // 2)
                eye2 = (cx + dy * offset + dx * offset // 2, cy + dx * offset + dy * offset // 2)
                pygame.draw.circle(surface, (10, 10, 10), eye1, eye_size)
                pygame.draw.circle(surface, (10, 10, 10), eye2, eye_size)

            # small outline so segments don't blur into one blob when overlapping in color
            pygame.draw.rect(surface, (0, 0, 0), rect, width=1, border_radius=6)

        # if shield is on, draw a glowing-ish outline around the head
        if self.shield_active:
            head_x, head_y = self.body[0]
            rect = pygame.Rect(head_x * tile_size, head_y * tile_size + offset_y, tile_size, tile_size)
            pygame.draw.rect(surface, (180, 180, 255), rect.inflate(6, 6), width=2, border_radius=8)
