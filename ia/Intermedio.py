import random
from collections import defaultdict

class Intermedio:
    def __init__(self, game):
        self.game = game
        self.first_move = True

    def make_move(self):
        try:
            if not hasattr(self.game, 'board') or not hasattr(self.game.board, 'board_list'):
                return False
                
            # Acceso seguro a las dimensiones
            board = self.game.board
            cols = len(board.board_list)
            rows = len(board.board_list[0]) if cols > 0 else 0

            # Primer movimiento en el centro
            if self.first_move:
                center_x = cols // 2
                center_y = rows // 2
                self.first_move = False
                return board.dig(center_x, center_y)

            # Lógica intermedia mejorada
            safe_move = self.find_safe_move()
            if safe_move:
                return safe_move
                
            return self.make_random_move()

        except Exception as e:
            print(f"Error en IA Intermedia: {e}")
            return False

    def find_safe_move(self):
        board = self.game.board
        for x in range(len(board.board_list)):
            for y in range(len(board.board_list[0])):
                tile = board.board_list[x][y]
                if tile.revealed and tile.type.isdigit():
                    num = int(tile.type)
                    neighbors = self.get_neighbors(x, y)
                    # ... resto de la lógica ...
        return None

    def get_neighbors(self, x, y):
        # Implementación segura
        neighbors = []
        directions = [(-1,-1), (-1,0), (-1,1),
                     (0,-1),          (0,1),
                     (1,-1),  (1,0),  (1,1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(self.game.board.board_list) and 0 <= ny < len(self.game.board.board_list[0]):
                neighbors.append((nx, ny))
        return neighbors

    def make_random_move(self):
        # Implementación segura
        hidden = []
        for x in range(len(self.game.board.board_list)):
            for y in range(len(self.game.board.board_list[0])):
                tile = self.game.board.board_list[x][y]
                if not tile.revealed and not tile.flagged:
                    hidden.append((x, y))
        
        return random.choice(hidden) if hidden else None