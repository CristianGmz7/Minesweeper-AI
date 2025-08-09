import tensorflow as tf
from game.game import Game
from agents.hybrid_agent import HybridAgent
from training.train import board_to_state
import pygame
from settings import TILESIZE, TOP_PANEL_HEIGHT, ROWS, COLS  # Importar configuraciones

class AIGame(Game):
    def __init__(self, model_path):
        super().__init__()
        self.model = tf.keras.models.load_model(model_path)
        self.agent = HybridAgent(self.model)
        self.auto_play = False
        self.last_action_time = 0  # Para controlar la velocidad de juego
    
    def events(self):
        current_time = pygame.time.get_ticks()
        
        # Ejecutar acciones de la IA cada 500ms
        if self.auto_play and current_time - self.last_action_time > 500:
            state = board_to_state(self.screen, self.tile_analyzer)
            action = self.agent.predict_action(state)
            
            if action:
                action_type, x, y = action
                # Simular clic
                if action_type == 'left':
                    self.handle_left_click(x, y)
                elif action_type == 'right':
                    self.handle_right_click(x, y)
                
                self.last_action_time = current_time
                # Actualizar pantalla inmediatamente después de la acción
                self.draw()
                pygame.display.flip()
        
        super().events()
    
    def handle_left_click(self, x, y):
        """Implementa la lógica de clic izquierdo en la posición (x, y)"""
        # Convertir coordenadas de casilla a coordenadas de pantalla
        mx = x * TILESIZE + TILESIZE // 2
        my = y * TILESIZE + TOP_PANEL_HEIGHT + TILESIZE // 2
        
        # Verificar que el clic es dentro del tablero
        if my < TOP_PANEL_HEIGHT or x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return
        
        # Lógica de clic izquierdo (similar a la clase base)
        tile = self.board.board_list[x][y]
        
        # Si la casilla está marcada con bandera, ignorar clic
        if tile.flagged:
            return
        
        # Si es el primer clic, iniciar temporizador
        if self.first_click:
            self.first_click = False
            self.timer_started = True
            self.elapsed_time = 0
            self.update_timer()
        
        # Revelar la casilla
        if not self.board.dig(x, y):
            # Si era una mina, terminar juego
            self.end_game(False)
        elif self.check_win():
            # Si ganó, terminar juego
            self.end_game(True)
    
    def handle_right_click(self, x, y):
        """Implementa la lógica de clic derecho en la posición (x, y)"""
        # Convertir coordenadas de casilla a coordenadas de pantalla
        mx = x * TILESIZE + TILESIZE // 2
        my = y * TILESIZE + TOP_PANEL_HEIGHT + TILESIZE // 2
        
        # Verificar que el clic es dentro del tablero
        if my < TOP_PANEL_HEIGHT or x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return
        
        # Lógica de clic derecho (similar a la clase base)
        tile = self.board.board_list[x][y]
        
        # Solo se puede marcar casillas no reveladas
        if not tile.revealed:
            # Cambiar estado de bandera
            tile.flagged = not tile.flagged
            
            # Actualizar contador de banderas
            if tile.flagged:
                self.flags_remaining -= 1
            else:
                self.flags_remaining += 1
            
            self.update_flag_counter()

if __name__ == "__main__":
    ai_game = AIGame('models/minesweeper_model.h5')
    ai_game.auto_play = True
    ai_game.run()