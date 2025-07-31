import random
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
            self.rect = self.image.get_rect(center=(self.x, self.y))  # Actualizar rect
            
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
        # CASO ESPECIAL: Bandera incorrecta (TileNotMine)
        if self.revealed and self.image == tile_not_mine:
            board_surface.blit(tile_not_mine, (self.x, self.y - TOP_PANEL_HEIGHT))
        # Casilla revelada normal
        elif not self.flagged and self.revealed:
            board_surface.blit(self.image, (self.x, self.y - TOP_PANEL_HEIGHT))
        # Casilla con bandera
        elif self.flagged and not self.revealed:
            board_surface.blit(tile_flag, (self.x, self.y - TOP_PANEL_HEIGHT))
        # Casilla no revelada
        elif not self.revealed:
            board_surface.blit(tile_unknown, (self.x, self.y - TOP_PANEL_HEIGHT))

    def __repr__(self):
        return self.type


class Board:
    def __init__(self):
        self.board_surface = pygame.Surface((WIDTH, HEIGHT - TOP_PANEL_HEIGHT))
        self.board_list = [[Tile(col, row, tile_empty, ".") for row in range(ROWS)] for col in range(COLS)]
        self.place_mines()
        self.place_clues()
        self.dug = []

    def place_mines(self):
        for _ in range(AMOUNT_MINES):
            while True:
                x = random.randint(0, ROWS-1)
                y = random.randint(0, COLS-1)

                if self.board_list[x][y].type == ".":
                    self.board_list[x][y].image = tile_mine
                    self.board_list[x][y].type = "X"
                    break

    def place_clues(self):
        for x in range(ROWS):
            for y in range(COLS):
                if self.board_list[x][y].type != "X":
                    total_mines = self.check_neighbours(x, y)
                    if total_mines > 0:
                        self.board_list[x][y].image = tile_numbers[total_mines-1]
                        self.board_list[x][y].type = "C"
                    else:
                        self.board_list[x][y].image = tile_empty
                        self.board_list[x][y].type = "/"

    @staticmethod
    def is_inside(x, y):
        return 0 <= x < ROWS and 0 <= y < COLS

    def check_neighbours(self, x, y):
        total_mines = 0
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                if x_offset == 0 and y_offset == 0:
                    continue
                neighbour_x = x + x_offset
                neighbour_y = y + y_offset
                if self.is_inside(neighbour_x, neighbour_y) and self.board_list[neighbour_x][neighbour_y].type == "X":
                    total_mines += 1

        return total_mines

    def draw(self, screen):
        self.board_surface.fill(BGCOLOUR)
        for row in self.board_list:
            for tile in row:
                tile.draw(self.board_surface)
        screen.blit(self.board_surface, (0, TOP_PANEL_HEIGHT))

    def dig(self, x, y):
        # Si la casilla tiene bandera, no hacer nada
        if self.board_list[x][y].flagged:
            return True
            
        self.dug.append((x, y))
        if self.board_list[x][y].type == "X":
            self.board_list[x][y].revealed = True
            self.board_list[x][y].image = tile_exploded
            return False
        elif self.board_list[x][y].type == "C":
            self.board_list[x][y].revealed = True
            return True

        self.board_list[x][y].revealed = True

        # Expandir solo a casillas sin bandera
        for row in range(max(0, x-1), min(ROWS-1, x+1) + 1):
            for col in range(max(0, y-1), min(COLS-1, y+1) + 1):
                # Solo expandir a casillas no marcadas con bandera
                if not self.board_list[row][col].flagged and (row, col) not in self.dug:
                    self.dig(row, col)
        return True

    def display_board(self):
        for row in self.board_list:
            print(row)