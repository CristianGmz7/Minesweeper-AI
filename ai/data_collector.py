import numpy as np
import pickle
import os
from collections import deque
from settings import ROWS, COLS
import pygame
from game.game import Game
from ai.model import board_to_state
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import WIDTH, HEIGHT
from agents.rules_agent import RulesAgent

class DataCollector:
    def __init__(self, max_samples=50000):
        self.states = deque(maxlen=max_samples)
        self.left_targets = deque(maxlen=max_samples)
        self.right_targets = deque(maxlen=max_samples)
        self.sample_count = 0
        self.rules_agent = RulesAgent()  
        
    def add_sample(self, state, action_type, row, col):
        # Crear targets
        left_target = np.zeros(ROWS * COLS, dtype=np.float32)
        right_target = np.zeros(ROWS * COLS, dtype=np.float32)
        
        # Convertir (row, col) a índice flat
        target_index = row * COLS + col
        
        if action_type == 'left':
            left_target[target_index] = 1.0
        elif action_type == 'right':
            right_target[target_index] = 1.0
        else:
            print(f"⚠️ Tipo de acción inválido: {action_type}")
            return
        
        # Guardar muestra
        self.states.append(state.copy())
        self.left_targets.append(left_target.copy())
        self.right_targets.append(right_target.copy())
        self.sample_count += 1
        
        if self.sample_count % 100 == 0:
            print(f"📊 Muestras recolectadas: {self.sample_count}")
    
    def get_dataset(self):
        """Retorna el dataset para entrenamiento"""
        if len(self.states) == 0:
            print("❌ No hay datos para entrenar")
            return None, None
            
        X = np.array(self.states)
        y = [np.array(self.left_targets), np.array(self.right_targets)]
        
        print(f"📊 Dataset creado: {len(X)} muestras")
        return X, y
    
    def save_data(self, filepath="data/training_data.pkl"):
        """Guarda los datos recolectados"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            'states': list(self.states),
            'left_targets': list(self.left_targets),
            'right_targets': list(self.right_targets),
            'sample_count': self.sample_count
        }
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            print(f"💾 Datos guardados en {filepath}")
        except Exception as e:
            print(f"❌ Error guardando datos: {e}")
    
    def load_data(self, filepath="data/training_data.pkl"):
        """Carga datos previamente guardados"""
        if not os.path.exists(filepath):
            print(f"📄 Archivo {filepath} no encontrado")
            return
        
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.states.extend(data['states'])
            self.left_targets.extend(data['left_targets'])
            self.right_targets.extend(data['right_targets'])
            self.sample_count = len(self.states)
            
            print(f"📂 Datos cargados: {self.sample_count} muestras")
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
    
    def clear_data(self):
        """Limpia todos los datos"""
        self.states.clear()
        self.left_targets.clear()
        self.right_targets.clear()
        self.sample_count = 0
        print("🗑️ Datos limpiados")

    def _print_board_state(self, game):
        """Muestra el estado actual del tablero de forma segura"""
        try:
            print("\nEstado del tablero:")
            for row in range(ROWS):
                for col in range(COLS):
                    try:
                        tile_type, _, _ = game.tile_analyzer.analyze_tile(game.screen, col, row)
                        print(f"({row},{col}): {tile_type[:15]:<15}", end=" | ")
                    except Exception as e:
                        print(f"({row},{col}): Error {str(e)[:10]:<10}", end=" | ")
                print()
        except Exception as e:
            print(f"Error al imprimir estado del tablero: {e}")

    def generate_rule_based_data(self, num_samples=5000):
        print("🎮 Iniciando generación automática de datos...")
        
        samples_generated = 0
        games_played = 0
        
        # Asegurar que pygame esté inicializado
        if not pygame.get_init():
            pygame.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        while samples_generated < num_samples and games_played < 1000:
            try:
                game = Game()
                print(f"\n🔹 Juego {games_played + 1}")
                
                # Mostrar estado inicial de depuración
                game_state, _, _ = game.tile_analyzer.analyze_face_state(game.screen)
                print(f"Estado inicial: {game_state}")
                
                # Mostrar tablero inicial (solo si hay menos de 5 juegos para no saturar)
                if games_played < 5:
                    self._print_board_state(game)
                
                moves_in_game = 0
                
                while game.game_active and moves_in_game < 200:
                    try:
                        # Obtener estado actual
                        current_state = board_to_state(game.screen, game.tile_analyzer)
                        
                        # Obtener acción de las reglas
                        action = self.rules_agent.predict_action(current_state, game.flags_remaining)
                        
                        if not action:
                            if games_played < 3:  # Solo mostrar en los primeros juegos
                                print("⚠️ No se encontraron acciones válidas")
                            break
                        
                        action_type, row, col = action
                        
                        # Registrar muestra
                        self.add_sample(current_state, action_type, row, col)
                        samples_generated += 1
                        
                        # Ejecutar acción
                        if action_type == 'left':
                            if not game.board.dig(col, row):
                                break
                        elif action_type == 'right':
                            tile = game.board.board_list[col][row]
                            if not tile.revealed and not tile.flagged and game.flags_remaining > 0:
                                tile.flagged = True
                                game.flags_remaining -= 1
                        
                        # Actualizar pantalla
                        game.draw()
                        pygame.display.flip()
                        moves_in_game += 1
                        
                    except Exception as e:
                        print(f"⚠️ Error durante el juego: {e}")
                        break
                    
                games_played += 1
                
                # Mostrar progreso cada 10 juegos
                if games_played % 10 == 0:
                    print(f"📊 Progreso: {games_played} juegos | {samples_generated} muestras")
                    
            except Exception as e:
                print(f"⚠️ Error al iniciar juego: {e}")
                games_played += 1
                continue
        
        print(f"\n✅ Finalizado: {samples_generated} muestras de {games_played} juegos")
        return samples_generated