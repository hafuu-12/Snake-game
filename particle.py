"""
particle.py

Small visual effects live here - the little burst of dots when you eat
food, and the floating circles that drift around in the background of
the main menu (purely decorative, doesn't affect gameplay at all).
"""

import random
import pygame


class Particle:
    """One tiny dot that flies outward and fades away."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # random direction, random speed - gives it that little "pop" look
        speed = random.uniform(1.0, 3.2)
        self.vx = speed * (1 if random.random() > 0.5 else -1) * random.random()
        self.vy = speed * (1 if random.random() > 0.5 else -1) * random.random()
        self.life = 26  # frames, not ms - close enough at 60fps
        self.max_life = self.life
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # slight gravity, makes it feel a little more natural
        self.life -= 1

    def is_dead(self):
        return self.life <= 0

    def draw(self, surface):
        if self.life <= 0:
            return
        # shrink the particle as it dies instead of just popping out of existence
        fade = self.life / self.max_life
        size = max(1, int(self.size * fade))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class ParticleSystem:
    """Just keeps a list of Particle objects and updates/draws all of them."""

    def __init__(self):
        self.particles = []

    def burst(self, x, y, color, count=14):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        for p in self.particles:
            p.update()
        # clean out dead ones - probably could do this less often but
        # the lists never get big enough for it to matter
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


class FloatingShape:
    """
    A slow drifting circle used to make the main menu background feel a
    little alive instead of just a flat color. Bounces off the screen edges.
    """

    def __init__(self, screen_w, screen_h):
        self.x = random.randint(0, screen_w)
        self.y = random.randint(0, screen_h)
        self.radius = random.randint(8, 26)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        # avoid spawning a shape with basically zero velocity
        if abs(self.vx) < 0.1:
            self.vx = 0.2
        if abs(self.vy) < 0.1:
            self.vy = 0.2
        self.alpha = random.randint(25, 60)

    def update(self, screen_w, screen_h):
        self.x += self.vx
        self.y += self.vy
        if self.x < -self.radius or self.x > screen_w + self.radius:
            self.vx *= -1
        if self.y < -self.radius or self.y > screen_h + self.radius:
            self.vy *= -1

    def draw(self, surface, color):
        # draw onto a small temp surface so we can use alpha transparency
        temp = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp, (*color, self.alpha), (self.radius, self.radius), self.radius)
        surface.blit(temp, (self.x - self.radius, self.y - self.radius))
