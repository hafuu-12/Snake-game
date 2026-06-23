"""
button.py

Simple clickable button for all the menu screens, plus a tiny Menu
wrapper that just groups a bunch of buttons together so I'm not
copy-pasting the same hover/click logic in every single screen function.
"""

import pygame


class Button:
    def __init__(self, rect, text, action, font, base_color=(70, 70, 70),
                 hover_color=(100, 100, 100), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        # "action" is just a string the Game class checks to decide what
        # to do - e.g. "start", "exit", "theme_neon". Kept it simple instead
        # of passing actual function callbacks around.
        self.action = action
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, surface, mouse_pos):
        hovering = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if hovering else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        # thin outline, just looks a bit nicer than a flat block
        pygame.draw.rect(surface, (20, 20, 20), self.rect, width=2, border_radius=10)

        txt_surf = self.font.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)
        return hovering

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class Menu:
    """Holds a list of Button objects for one screen (main menu, settings, etc)."""

    def __init__(self):
        self.buttons = []

    def add_button(self, rect, text, action, font, **kwargs):
        self.buttons.append(Button(rect, text, action, font, **kwargs))

    def draw(self, surface, mouse_pos):
        for b in self.buttons:
            b.draw(surface, mouse_pos)

    def get_clicked_action(self, mouse_pos):
        # returns the action string of whatever button was clicked, or None
        for b in self.buttons:
            if b.is_clicked(mouse_pos):
                return b.action
        return None

    def clear(self):
        self.buttons = []
