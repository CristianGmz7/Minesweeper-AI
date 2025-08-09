import sys
import os

# Añadir el directorio padre al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game import Game
from settings import TOP_PANEL_HEIGHT, TILESIZE, ROWS, COLS
from training.train import board_to_state
import pygame
import numpy as np


class TrainingGame(Game):
    def __init__(self, collector=None):
        super().__init__()
        self.collector = collector
        self.last_state = None
    
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if my > TOP_PANEL_HEIGHT:
                    # Guardar estado antes de la acción
                    self.last_state = board_to_state(self.screen, self.tile_analyzer)
        
        super().events()
        
        # Guardar datos después de la acción
        if self.collector and self.last_state is not None:
            mx, my = pygame.mouse.get_pos()
            tile_x, tile_y = mx // TILESIZE, (my - TOP_PANEL_HEIGHT) // TILESIZE
            
            left_target = np.zeros((ROWS, COLS))
            right_target = np.zeros((ROWS, COLS))
            
            if pygame.mouse.get_pressed()[0]:  # Clic izquierdo
                left_target[tile_x, tile_y] = 1.0
            elif pygame.mouse.get_pressed()[2]:  # Clic derecho
                right_target[tile_x, tile_y] = 1.0
            
            self.collector.add_sample(
                state=self.last_state,
                left_target=left_target.flatten(),
                right_target=right_target.flatten()
            )
            self.last_state = None