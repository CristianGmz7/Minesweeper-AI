#sprites.py
import pygame
from settings import *

class Digit:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.images = {
            'empty': tile_time_empty,
            'minus': tile_time_minus
        }
        for i in range(10):
            self.images[str(i)] = tile_digits[i]
        self.image = self.images['minus']
        
    def set_digit(self, digit):
        if digit in self.images:
            self.image = self.images[digit]
            
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

class FaceButton:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.states = {
            'normal': tile_face_smile,
            'win': tile_face_win,
            'loose': tile_face_loose
        }
        self.image = self.states['normal']
        self.rect = self.image.get_rect(center=(x, y))
        
    def change_state(self, state):
        if state in self.states:
            self.image = self.states[state]
            self.rect = self.image.get_rect(center=(self.x, self.y))
            
    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

class Tile:
    def __init__(self, x, y, image, type, revealed=False, flagged=False):
        self.x, self.y = x * TILESIZE, y * TILESIZE + TOP_PANEL_HEIGHT
        self.image = image
        self.type = type
        self.revealed = revealed
        self.flagged = flagged
        self.rect = pygame.Rect(self.x, self.y, TILESIZE, TILESIZE)

    def draw(self, board_surface):
        if self.revealed and self.image == tile_not_mine:
            board_surface.blit(tile_not_mine, (self.x, self.y - TOP_PANEL_HEIGHT))
        elif not self.flagged and self.revealed:
            board_surface.blit(self.image, (self.x, self.y - TOP_PANEL_HEIGHT))
        elif self.flagged and not self.revealed:
            board_surface.blit(tile_flag, (self.x, self.y - TOP_PANEL_HEIGHT))
        elif not self.revealed:
            board_surface.blit(tile_unknown, (self.x, self.y - TOP_PANEL_HEIGHT))

    def __repr__(self):
        return self.type