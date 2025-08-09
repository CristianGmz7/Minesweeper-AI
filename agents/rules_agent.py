from agents.base_agent import BaseAgent
from settings import ROWS, COLS

class RulesAgent(BaseAgent):
    def _init_(self):
        super()._init_()
    
    def predict_action(self, state, flags_remaining=None):
        """
        Implementa todas las reglas lógicas del Buscaminas con control de banderas.
        
        Args:
            state: Estado del tablero (array numpy)
            flags_remaining: Número de banderas disponibles (opcional)
            
        Returns:
            Tupla (tipo_accion, x, y) o None si no hay acción válida
        """
        board = state[..., :5]  # Características del tablero
        game_active = state[0, 0, 5]  # Estado del juego
        
        if game_active < 0.5:
            return None  # Juego no activo
        
        # Regla 1: Si el número es igual a casillas ocultas adyacentes, todas son minas
        action = self._apply_rule_hidden_mines(board, flags_remaining)
        if action:
            return action
        
        # Regla 2: Si el número es igual a banderas adyacentes, las demás son seguras
        action = self._apply_rule_safe_tiles(board)
        if action:
            return action
        
        # Regla 3: Análisis de fronteras para configuraciones complejas
        action = self._apply_border_analysis(board, flags_remaining)
        if action:
            return action
        
        return None
    
    def _apply_rule_hidden_mines(self, board, flags_remaining):
        """Regla: Número == Casillas ocultas adyacentes => Todas son minas"""
        for x in range(ROWS):
            for y in range(COLS):
                if board[x, y, 2] > 0:  # Es un número
                    number = int(board[x, y, 4] * 8)
                    hidden_neighbors = self._get_hidden_neighbors(board, x, y)
                    
                    if len(hidden_neighbors) == number:
                        # Verificar si podemos colocar banderas
                        if flags_remaining is not None and len(hidden_neighbors) > flags_remaining:
                            continue  # No hay suficientes banderas
                        
                        # Todas las casillas ocultas deben ser minas
                        for nx, ny in hidden_neighbors:
                            if not self._has_flag(board, nx, ny):
                                return ('right', nx, ny)
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
                        for nx, ny in hidden_neighbors:
                            if not self._has_flag(board, nx, ny):
                                return ('left', nx, ny)
        return None
    
    def _apply_border_analysis(self, board, flags_remaining):
        """Análisis avanzado de fronteras con control de banderas"""
        border_tiles = self._get_border_tiles(board)
        
        for x, y in border_tiles:
            if board[x, y, 2] > 0:  # Es un número
                number = int(board[x, y, 4] * 8)
                hidden = self._get_hidden_neighbors(board, x, y)
                flags = self._get_flag_neighbors(board, x, y)
                
                remaining_mines = number - len(flags)
                
                if remaining_mines == 0:
                    for nx, ny in hidden:
                        if not self._has_flag(board, nx, ny):
                            return ('left', nx, ny)
                
                elif remaining_mines == len(hidden):
                    # Verificar banderas disponibles
                    if flags_remaining is not None and len(hidden) > flags_remaining:
                        continue
                        
                    for nx, ny in hidden:
                        if not self._has_flag(board, nx, ny):
                            return ('right', nx, ny)
        
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
    
    def _has_flag(self, board, x, y):
        """Verifica si una casilla tiene bandera"""
        return board[x, y, 1] > 0.5
    
    def _get_border_tiles(self, board):
        """Encuentra casillas fronterizas (números adyacentes a casillas ocultas)"""
        border_tiles = set()
        
        for x in range(ROWS):
            for y in range(COLS):
                if board[x, y, 2] > 0:  # Es un número
                    hidden = self._get_hidden_neighbors(board, x, y)
                    if hidden:
                        border_tiles.add((x, y))
        
        return border_tiles