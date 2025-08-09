#settings.py
# COLORS (r, g, b)
import pygame
import os

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
DARKGREEN = (0, 200, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BGCOLOUR = DARKGREY

# game settings
TILESIZE = 16  # Cambiado a 16px
ROWS = 9
COLS = 9
AMOUNT_MINES = 20
WIDTH = TILESIZE * ROWS
HEIGHT = TILESIZE * COLS + 50  # Added space for top panel
TOP_PANEL_HEIGHT = 50
FPS = 60
TITLE = "Minesweeper Clone"
DIGIT_WIDTH = 10  # Ajustado para assets más pequeños
DIGIT_HEIGHT = 20  # Ajustado para assets más pequeños
FACE_SIZE = 24  # Ajustado para assets más pequeños

# Load all assets
tile_numbers = []
for i in range(1, 9):
    tile_numbers.append(pygame.transform.scale(
        pygame.image.load(os.path.join("assets", f"Tile{i}.png")), 
        (TILESIZE, TILESIZE)
    ))

tile_empty = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileEmpty.png")), 
    (TILESIZE, TILESIZE)
)
tile_exploded = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileExploded.png")), 
    (TILESIZE, TILESIZE)
)
tile_flag = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileFlag.png")), 
    (TILESIZE, TILESIZE)
)
tile_mine = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileMine.png")), 
    (TILESIZE, TILESIZE)
)
tile_unknown = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileUnknown.png")), 
    (TILESIZE, TILESIZE)
)
tile_not_mine = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileNotMine.png")), 
    (TILESIZE, TILESIZE)
)

# Load face assets
tile_face_smile = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileFaceSmile.png")), 
    (FACE_SIZE, FACE_SIZE)
)

tile_face_loose = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileFaceLoose.png")), 
    (FACE_SIZE, FACE_SIZE)
)
tile_face_win = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileFaceWin.png")), 
    (FACE_SIZE, FACE_SIZE)
)

# Load digit assets
tile_digits = []
for i in range(10):
    tile_digits.append(pygame.transform.scale(
        pygame.image.load(os.path.join("assets", f"TileTime{i}.png")), 
        (DIGIT_WIDTH, DIGIT_HEIGHT)
    ))
    
tile_time_empty = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileTimeEmpty.png")), 
    (DIGIT_WIDTH, DIGIT_HEIGHT)
)
tile_time_minus = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "TileTimeMinus.png")), 
    (DIGIT_WIDTH, DIGIT_HEIGHT)
)