import random
import time

class Beginner:
    def __init__(self, game):
        self.game = game
        self.first_move = True

    def make_move(self):
        try:
            if not self.game.game_active:
                return False

            # Accede correctamente a las dimensiones del tablero
            cols = len(self.game.board.board_list)
            rows = len(self.game.board.board_list[0]) if cols > 0 else 0

            if self.first_move:
                x = cols // 2
                y = rows // 2
                self.first_move = False
                time.sleep(0.3)  # Pequeña pausa para visualización
                return self.game.board.dig(x, y)

            # Movimiento aleatorio seguro
            hidden_tiles = [
                (x, y) 
                for x in range(cols) 
                for y in range(rows)
                if not self.game.board.board_list[x][y].revealed 
                and not self.game.board.board_list[x][y].flagged
            ]

            if hidden_tiles:
                x, y = random.choice(hidden_tiles)
                time.sleep(0.3)
                return self.game.board.dig(x, y)
            return False

        except Exception as e:
            print(f"Error en IA Principiante: {e}")
            return False