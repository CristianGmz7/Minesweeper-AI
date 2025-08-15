from agents.base_agent import BaseAgent
from settings import ROWS, COLS
import random

class RulesAgent(BaseAgent):
    def __init__(self):
        super().__init__()
    
    def predict_action(self, state, flags_remaining=None):
        # Verificar si el juego está activo
        game_active = state[0, 0, 5] > 0.5
        if not game_active:
            return None
        
        if self._is_board_completely_hidden(state):
            return self._get_random_hidden_tile(state)
        
        # Regla 1: Números satisfechos - revelar casillas seguras
        safe_action = self._find_safe_tiles(state)
        if safe_action:
            return safe_action
        
        # Regla 2: Números con todas las minas identificadas - marcar minas
        mine_action = self._find_mines(state, flags_remaining)
        if mine_action:
            return mine_action
        
        random_action = self._get_random_hidden_tile(state)
        return random_action
    
    def _is_board_completely_hidden(self, state):
        """Verifica si todo el tablero está sin revelar"""
        for row in range(ROWS):
            for col in range(COLS):
                if state[row, col, 0] < 0.5:  # Si está revelado
                    return False
        return True
    
    def _get_random_hidden_tile(self, state):
        """Devuelve una casilla sin revelar aleatoria"""
        hidden_tiles = []
        for row in range(ROWS):
            for col in range(COLS):
                if state[row, col, 0] > 0.5:  # Si está sin revelar
                    hidden_tiles.append(('left', row, col))
        
        return random.choice(hidden_tiles) if hidden_tiles else None
    
    def _find_safe_tiles(self, state):
        """Encuentra casillas seguras para revelar"""
        for row in range(ROWS):
            for col in range(COLS):
                # Solo procesar casillas que son números revelados
                if not self._is_revealed_number(state, row, col):
                    continue
                
                number = self._get_number_value(state, row, col)
                if number == 0:
                    continue
                
                # Obtener vecinos
                hidden_neighbors = self._get_hidden_neighbors(state, row, col)
                flag_neighbors = self._get_flag_neighbors(state, row, col)
                
                # Si el número de banderas == número, las casillas ocultas son seguras
                if len(flag_neighbors) == number and hidden_neighbors:
                    target_row, target_col = hidden_neighbors[0]
                    return ('left', target_row, target_col)
        
        return None
    
    def _find_mines(self, state, flags_remaining):
        """Encuentra minas para marcar con banderas"""
        # Verificar si tenemos banderas disponibles
        if flags_remaining is not None and flags_remaining <= 0:
            return None
        
        for row in range(ROWS):
            for col in range(COLS):
                # Solo procesar casillas que son números revelados
                if not self._is_revealed_number(state, row, col):
                    continue
                
                number = self._get_number_value(state, row, col)
                if number == 0:
                    continue
                
                # Obtener vecinos
                hidden_neighbors = self._get_hidden_neighbors(state, row, col)
                flag_neighbors = self._get_flag_neighbors(state, row, col)
                
                # Si casillas ocultas + banderas == número, las ocultas son minas
                total_mines_around = len(hidden_neighbors) + len(flag_neighbors)
                if total_mines_around == number and hidden_neighbors:
                    # Verificar que no excedamos las banderas disponibles
                    if flags_remaining is not None and len(hidden_neighbors) > flags_remaining:
                        continue
                    
                    target_row, target_col = hidden_neighbors[0]
                    return ('right', target_row, target_col)
        
        return None
    
    def _is_revealed_number(self, state, row, col):
        """Verifica si una casilla es un número revelado"""
        # Características: [sin_revelar, bandera, es_numero, espacio_vacio, valor_numero, juego_activo]
        is_hidden = state[row, col, 0] > 0.5      # Sin revelar
        has_flag = state[row, col, 1] > 0.5       # Con bandera
        is_number = state[row, col, 2] > 0.5      # Es número
        
        # Es número revelado si: es_numero=True Y sin_revelar=False Y bandera=False
        return is_number and not is_hidden and not has_flag
    
    def _get_number_value(self, state, row, col):
        """Obtiene el valor numérico de una casilla"""
        if not self._is_revealed_number(state, row, col):
            return 0
        
        # El valor está normalizado (0-1), desnormalizar a 1-8
        normalized_value = state[row, col, 4]
        return int(round(normalized_value * 8))
    
    def _get_neighbors(self, row, col):
        """Obtiene las coordenadas de todas las casillas vecinas"""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                new_row = row + dr
                new_col = col + dc
                
                if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                    neighbors.append((new_row, new_col))
        
        return neighbors
    
    def _get_hidden_neighbors(self, state, row, col):
        """Obtiene vecinos que están sin revelar y sin bandera"""
        neighbors = self._get_neighbors(row, col)
        hidden = []
        
        for nr, nc in neighbors:
            is_hidden = state[nr, nc, 0] > 0.5    # Sin revelar
            has_flag = state[nr, nc, 1] > 0.5     # Con bandera
            
            if is_hidden and not has_flag:
                hidden.append((nr, nc))
        
        return hidden
    
    def _get_flag_neighbors(self, state, row, col):
        """Obtiene vecinos que tienen bandera"""
        neighbors = self._get_neighbors(row, col)
        flagged = []
        
        for nr, nc in neighbors:
            has_flag = state[nr, nc, 1] > 0.5     # Con bandera
            
            if has_flag:
                flagged.append((nr, nc))
        
        return flagged