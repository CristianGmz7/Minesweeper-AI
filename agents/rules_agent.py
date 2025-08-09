import numpy as np
from agents.base_agent import BaseAgent
from settings import ROWS, COLS  # Importar configuración del juego

class RulesAgent(BaseAgent):
    def __init__(self):
        super().__init__()
    
    def predict_action(self, state):
        """
        Implementa todas las reglas lógicas del Buscaminas.
        Devuelve una acción en formato ('left/right', x, y) o None si no hay acción obvia.
        """
        board = state[..., :5]  # Características del tablero
        game_active = state[0, 0, 5]  # Estado del juego
        
        if game_active < 0.5:
            return None  # Juego no activo
        
        # Regla 1: Si el número es igual a casillas ocultas adyacentes, todas son minas
        action = self._apply_rule_hidden_mines(board)
        if action:
            return action
        
        # Regla 2: Si el número es igual a banderas adyacentes, las demás son seguras
        action = self._apply_rule_safe_tiles(board)
        if action:
            return action
        
        # Regla 3: Análisis de fronteras para configuraciones complejas
        action = self._apply_border_analysis(board)
        if action:
            return action
        
        return None
    
    def _apply_rule_hidden_mines(self, board):
        """Regla: Número == Casillas ocultas adyacentes => Todas son minas"""
        for x in range(ROWS):
            for y in range(COLS):
                if board[x, y, 2] > 0:  # Es un número
                    number = int(board[x, y, 4] * 8)  # Convertir a valor real (1-8)
                    hidden_neighbors = self._get_hidden_neighbors(board, x, y)
                    
                    if len(hidden_neighbors) == number:
                        # Todas las casillas ocultas deben ser minas
                        return ('right', hidden_neighbors[0][0], hidden_neighbors[0][1])
        return None
    
    def _apply_rule_safe_tiles(self, board):
        """Regla: Número == Banderas adyacentes => Las demás casillas son seguras"""
        for x in range(ROWS):
            for y in range(COLS):
                if board[x, y, 2] > 0:  # Es un número
                    number = int(board[x, y, 4] * 8)
                    flag_neighbors = self._get_flag_neighbors(board, x, y)
                    hidden_neighbors = self._get_hidden_neighbors(board, x, y)
                    
                    if len(flag_neighbors) == number and hidden_neighbors:
                        # Todas las minas ya están marcadas, las demás son seguras
                        return ('left', hidden_neighbors[0][0], hidden_neighbors[0][1])
        return None
    
    def _apply_border_analysis(self, board):
        """
        Análisis avanzado de fronteras para configuraciones complejas.
        Implementa las reglas expertas mencionadas en el documento original.
        """
        border_tiles = self._get_border_tiles(board)
        
        for x, y in border_tiles:
            if board[x, y, 2] > 0:  # Es un número
                number = int(board[x, y, 4] * 8)
                hidden = self._get_hidden_neighbors(board, x, y)
                flags = self._get_flag_neighbors(board, x, y)
                
                remaining_mines = number - len(flags)
                
                if remaining_mines == 0:
                    if hidden:
                        return ('left', hidden[0][0], hidden[0][1])
                
                elif remaining_mines == len(hidden):
                    return ('right', hidden[0][0], hidden[0][1])
        
        return None
    
    def _get_neighbors(self, x, y):
        """Obtiene coordenadas de las casillas adyacentes"""
        neighbors = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < ROWS and 0 <= ny < COLS and (dx, dy) != (0, 0):
                    neighbors.append((nx, ny))
        return neighbors
    
    def _get_hidden_neighbors(self, board, x, y):
        """Obtiene casillas adyacentes no reveladas y sin bandera"""
        return [
            (nx, ny) for nx, ny in self._get_neighbors(x, y)
            if board[nx, ny, 0] > 0.5 and board[nx, ny, 1] < 0.5
        ]
    
    def _get_flag_neighbors(self, board, x, y):
        """Obtiene casillas adyacentes con bandera"""
        return [
            (nx, ny) for nx, ny in self._get_neighbors(x, y)
            if board[nx, ny, 1] > 0.5
        ]
    
    def _get_border_tiles(self, board):
        """
        Encuentra casillas fronterizas (números adyacentes a casillas ocultas).
        Estas son las más importantes para el análisis avanzado.
        """
        border_tiles = set()
        
        for x in range(ROWS):
            for y in range(COLS):
                if board[x, y, 2] > 0:  # Es un número
                    hidden = self._get_hidden_neighbors(board, x, y)
                    if hidden:
                        border_tiles.add((x, y))
        
        return border_tiles