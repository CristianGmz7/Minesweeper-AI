import tensorflow as tf
import numpy as np
import random
import pickle
from collections import deque
import os
import time

# ARREGLO CRÍTICO PARA TENSORFLOW
tf.config.run_functions_eagerly(True)

class ExpertAI:
    def __init__(self, game):
        self.game = game
        self.model = None
        self.first_move = True
        self.memory = deque(maxlen=5000)
        self.epsilon = 0.8
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.998
        self.gamma = 0.95
        self.batch_size = 32
        self.model_file = "ai_model.keras"
        self.memory_file = "ai_memory.pkl"
        self.stats_file = "ai_stats.pkl"
        
        # Variables de control
        self.last_state = None
        self.last_action = None
        self.move_count = 0
        self.games_played = 0
        self.last_move_time = 0
        self.move_delay = 0.8
        self.debug_mode = True
        self.training_enabled = True
        self.paused = False
        
        # Estadísticas
        self.wins = 0
        self.losses = 0
        self.flags_placed = 0
        self.correct_flags = 0
        self.mines_hit = 0
        
        self.load_state()
        self.print_status()

    def print_status(self):
        """Imprime el estado actual de la IA"""
        print(f"\n🤖 IA EXPERTA INICIALIZADA")
        print(f"📊 Juegos totales: {self.games_played}")
        print(f"🏆 Victorias: {self.wins} | 💥 Derrotas: {self.losses}")
        if self.flags_placed > 0:
            accuracy = (self.correct_flags / self.flags_placed) * 100
            print(f"🚩 Precisión banderas: {accuracy:.1f}% ({self.correct_flags}/{self.flags_placed})")
        print(f"🧠 Epsilon (exploración): {self.epsilon:.3f}")
        print(f"📚 Experiencias en memoria: {len(self.memory)}")
        print(f"⚙️ Delay entre movimientos: {self.move_delay}s")
        print(f"🔧 Debug mode: {'ON' if self.debug_mode else 'OFF'}")

    def safe_board_access(self):
        """Verifica acceso seguro al tablero"""
        try:
            return (hasattr(self.game, 'board') and 
                    hasattr(self.game.board, 'board_list') and 
                    len(self.game.board.board_list) > 0 and
                    len(self.game.board.board_list[0]) > 0)
        except:
            return False

    def get_board_dimensions(self):
        """Obtiene dimensiones del tablero de forma segura"""
        try:
            if self.safe_board_access():
                return len(self.game.board.board_list), len(self.game.board.board_list[0])
        except:
            pass
        return 0, 0

    def get_visual_representation(self):
        if not self.safe_board_access():
            return None
            
        board_representation = []
        cols, rows = self.get_board_dimensions()
        
        for x in range(cols):
            row = []
            for y in range(rows):
                tile = self.game.board.board_list[x][y] 
                if tile.revealed:
                    if tile.type == "X":
                        row.append(-1)  # Mina
                    elif tile.type.isdigit():
                        row.append(int(tile.type))  # Número 0-8
                    else:
                        row.append(0)  # Vacío
                elif tile.flagged:
                    row.append(9)  # Bandera
                else:
                    row.append(10)  # No revelado
            board_representation.append(row)
        
        # Convertir a array plano para la red neuronal
        return np.array(board_representation).flatten() 
    
    def initialize_model(self):
        """Inicializa modelo con mejor manejo de errores"""
        if self.model is None and self.safe_board_access():
            try:
                cols, rows = self.get_board_dimensions()
                input_shape = cols * rows * 3
                
                if os.path.exists(self.model_file):
                    try:
                        self.model = tf.keras.models.load_model(self.model_file)
                        print("✅ Modelo cargado correctamente")
                        # Verificar compatibilidad del modelo
                        test_input = np.zeros((1, input_shape))
                        _ = self.model.predict(test_input, verbose=0)
                    except Exception as e:
                        print(f"❌ Error cargando modelo ({e}), creando uno nuevo...")
                        self.build_model(input_shape)
                else:
                    self.build_model(input_shape)
            except Exception as e:
                print(f"❌ Error inicializando modelo: {e}")

    def build_model(self, input_shape):
        """Construye modelo más robusto"""
        try:
            self.model = tf.keras.Sequential([
                tf.keras.layers.Dense(256, activation='relu', input_shape=(input_shape,)),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.1),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(input_shape//3, activation='linear')
            ])
            
            optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
            
            self.model.compile(
                optimizer=optimizer,
                loss='mse',
                metrics=['mae']
            )
            
            print("🆕 Modelo nuevo creado correctamente")
            
        except Exception as e:
            print(f"❌ Error creando modelo: {e}")
            self.model = None

    def load_state(self):
        """Carga estado con mejor manejo de errores"""
        # Cargar memoria
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'rb') as f:
                    memory_data = pickle.load(f)
                    if isinstance(memory_data, list):
                        self.memory = deque(memory_data, maxlen=5000)
                    else:
                        self.memory = deque(maxlen=5000)
                print(f"✅ Memoria cargada: {len(self.memory)} experiencias")
        except Exception as e:
            print(f"⚠️ Error cargando memoria: {e}")
            self.memory = deque(maxlen=5000)
        
        # Cargar estadísticas
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'rb') as f:
                    stats = pickle.load(f)
                    if isinstance(stats, dict):
                        self.epsilon = float(stats.get('epsilon', 0.8))
                        self.games_played = int(stats.get('games_played', 0))
                        self.wins = int(stats.get('wins', 0))
                        self.losses = int(stats.get('losses', 0))
                        self.flags_placed = int(stats.get('flags_placed', 0))
                        self.correct_flags = int(stats.get('correct_flags', 0))
                        self.mines_hit = int(stats.get('mines_hit', 0))
                print("✅ Estadísticas cargadas")
        except Exception as e:
            print(f"⚠️ Error cargando estadísticas: {e}")

    def save_state(self):
        """Guardado mejorado con validación"""
        try:
            saved_components = []
            
            # Guardar modelo
            if self.model is not None:
                try:
                    # Crear directorio si no existe
                    os.makedirs(os.path.dirname(self.model_file) if os.path.dirname(self.model_file) else '.', exist_ok=True)
                    self.model.save(self.model_file, save_format='keras')
                    saved_components.append("modelo")
                except Exception as e:
                    print(f"❌ Error guardando modelo: {e}")
            
            # Guardar memoria
            try:
                memory_to_save = list(self.memory)[-2000:]  # Últimas 2000 experiencias
                with open(self.memory_file, 'wb') as f:
                    pickle.dump(memory_to_save, f, protocol=pickle.HIGHEST_PROTOCOL)
                saved_components.append("memoria")
            except Exception as e:
                print(f"❌ Error guardando memoria: {e}")
            
            # Guardar estadísticas
            try:
                stats_dict = {
                    'epsilon': float(self.epsilon),
                    'games_played': int(self.games_played),
                    'wins': int(self.wins),
                    'losses': int(self.losses),
                    'flags_placed': int(self.flags_placed),
                    'correct_flags': int(self.correct_flags),
                    'mines_hit': int(self.mines_hit)
                }
                
                with open(self.stats_file, 'wb') as f:
                    pickle.dump(stats_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
                saved_components.append("estadísticas")
            except Exception as e:
                print(f"❌ Error guardando estadísticas: {e}")
            
            # Reporte de guardado
            if saved_components:
                win_rate = (self.wins / max(self.games_played, 1)) * 100
                flag_accuracy = (self.correct_flags / max(self.flags_placed, 1)) * 100
                
                print(f"\n💾 GUARDADO EXITOSO ({', '.join(saved_components)})")
                print(f"   📊 Juegos: {self.games_played}")
                print(f"   🏆 Tasa de victoria: {win_rate:.1f}%")
                print(f"   🚩 Precisión banderas: {flag_accuracy:.1f}%")
                print(f"   🧠 Epsilon: {self.epsilon:.3f}")
            else:
                print("❌ No se pudo guardar ningún componente")
                
        except Exception as e:
            print(f"❌ Error crítico en guardado: {e}")

    def make_move(self):
        """Método principal optimizado con mejor manejo de errores"""
        try:
            if self.paused:
                return False

            current_time = time.time()
            if current_time - self.last_move_time < self.move_delay:
                return False
            self.last_move_time = current_time

            if not self.game.game_active or not self.safe_board_access():
                if self.last_state is not None:
                    self.process_game_end()
                return False
                
            self.initialize_model()
            self.move_count += 1
            
            if self.debug_mode and self.move_count % 20 == 0:
                print(f"\n--- MOVIMIENTO #{self.move_count} ---")
                self.analyze_board()
            
            # Primer movimiento
            if self.first_move:
                return self.make_first_move()
            
            # Estado actual
            current_state = self.board_to_state()
            if current_state is None:
                return False

            # Procesar experiencia anterior
            if self.last_state is not None and self.last_action is not None:
                reward = self.calculate_reward()
                self.remember(self.last_state, self.last_action, reward, current_state, False)

            # 1. Buscar minas definitas
            mine_positions = self.find_all_definite_mines()
            if mine_positions:
                return self.place_flag(mine_positions[0], current_state)

            # 2. Buscar movimientos seguros
            safe_positions = self.find_all_safe_moves()
            if safe_positions:
                return self.make_safe_move(safe_positions[0], current_state)

            # 3. IA o exploración
            return self.make_ai_or_random_move(current_state)
                    
        except Exception as e:
            print(f"❌ ERROR en make_move: {e}")
            return self.emergency_random_move()

    def make_first_move(self):
        """Primer movimiento optimizado"""
        try:
            cols, rows = self.get_board_dimensions()
            self.first_move = False
            center_x, center_y = cols//2, rows//2
            
            if self.debug_mode:
                print(f"🎯 PRIMER MOVIMIENTO: Centro ({center_x}, {center_y})")
            
            self.last_state = self.board_to_state()
            self.last_action = self.position_to_action(center_x, center_y)
            return self.game.board.dig(center_x, center_y)
        except Exception as e:
            print(f"Error en primer movimiento: {e}")
            return False

    def place_flag(self, position, current_state):
        """Coloca bandera con validación"""
        try:
            x, y = position
            if not self.safe_board_access():
                return False
                
            tile = self.game.board.board_list[x][y]
            
            if not tile.flagged and not tile.revealed and self.game.flags_remaining > 0:
                tile.flagged = True
                self.game.flags_remaining -= 1
                self.game.update_flag_counter()
                self.flags_placed += 1
                
                # Verificar corrección (si es posible)
                if hasattr(tile, 'type') and tile.type == "X":
                    self.correct_flags += 1
                
                if self.debug_mode:
                    accuracy = (self.correct_flags / self.flags_placed) * 100 if self.flags_placed > 0 else 0
                    print(f"🚩 BANDERA #{self.flags_placed} en ({x}, {y}) - Precisión: {accuracy:.1f}%")
                
                # Experiencia positiva
                action = self.position_to_action(x, y)
                self.remember(current_state, action, 10.0, current_state, False)
                return True
        except Exception as e:
            print(f"Error colocando bandera: {e}")
        return False

    def make_safe_move(self, position, current_state):
        """Movimiento seguro con validación"""
        try:
            x, y = position
            
            if self.debug_mode:
                print(f"✅ MOVIMIENTO SEGURO en ({x}, {y})")
                
            self.last_state = current_state
            self.last_action = self.position_to_action(x, y)
            return self.game.board.dig(x, y)
        except Exception as e:
            print(f"Error en movimiento seguro: {e}")
            return False

    def make_ai_or_random_move(self, current_state):
        """Movimiento con IA o aleatorio mejorado"""
        try:
            if self.model is None or np.random.rand() <= self.epsilon:
                # Exploración
                move_pos = self.make_smart_random_move()
                if move_pos:
                    x, y = move_pos
                    if self.debug_mode and self.move_count % 30 == 0:
                        print(f"🎲 EXPLORACIÓN en ({x}, {y})")
                        
                    self.last_state = current_state
                    self.last_action = self.position_to_action(x, y)
                    return self.game.board.dig(x, y)
            else:
                # Red neuronal
                try:
                    q_values = self.model.predict(current_state[np.newaxis], verbose=0)[0]
                    valid_actions = self.get_valid_actions()
                    
                    if valid_actions:
                        # Filtrar acciones válidas
                        valid_q_values = [(action, q_values[action] if action < len(q_values) else -999) 
                                        for action in valid_actions]
                        best_action = max(valid_q_values, key=lambda x: x[1])[0]
                        
                        x, y = self.action_to_position(best_action)
                        
                        if self.debug_mode and self.move_count % 30 == 0:
                            q_value = q_values[best_action] if best_action < len(q_values) else 0
                            print(f"🧠 RED NEURONAL en ({x}, {y}) - Q: {q_value:.3f}")
                        
                        self.last_state = current_state
                        self.last_action = best_action
                        return self.game.board.dig(x, y)
                except Exception as e:
                    if self.debug_mode:
                        print(f"Error en red neuronal: {e}")
                    return self.make_smart_random_move_fallback(current_state)
        except Exception as e:
            print(f"Error en movimiento IA: {e}")
            
        return False

    def make_smart_random_move_fallback(self, current_state):
        """Fallback para movimiento aleatorio"""
        try:
            move_pos = self.make_smart_random_move()
            if move_pos:
                x, y = move_pos
                self.last_state = current_state
                self.last_action = self.position_to_action(x, y)
                return self.game.board.dig(x, y)
        except Exception as e:
            print(f"Error en fallback: {e}")
        return False

    def emergency_random_move(self):
        """Movimiento de emergencia mejorado"""
        try:
            if not self.safe_board_access():
                return False
                
            cols, rows = self.get_board_dimensions()
            available_moves = []
            
            for x in range(cols):
                for y in range(rows):
                    tile = self.game.board.board_list[x][y]
                    if not tile.revealed and not tile.flagged:
                        available_moves.append((x, y))
            
            if available_moves:
                x, y = random.choice(available_moves)
                print(f"🚨 MOVIMIENTO DE EMERGENCIA en ({x}, {y})")
                return self.game.board.dig(x, y)
        except Exception as e:
            print(f"Error en emergencia: {e}")
        return False

    def find_all_definite_mines(self):
        """Encuentra minas definitas con mejor validación"""
        definite_mines = []
        try:
            if not self.safe_board_access():
                return definite_mines
            
            cols, rows = self.get_board_dimensions()
            
            for x in range(cols):
                for y in range(rows):
                    try:
                        tile = self.game.board.board_list[x][y]
                        if tile.revealed and tile.type.isdigit() and tile.type != '0':
                            num = int(tile.type)
                            neighbors = self.get_neighbors(x, y)
                            
                            hidden_neighbors = []
                            flagged_count = 0
                            
                            for nx, ny in neighbors:
                                neighbor_tile = self.game.board.board_list[nx][ny]
                                if neighbor_tile.flagged:
                                    flagged_count += 1
                                elif not neighbor_tile.revealed:
                                    hidden_neighbors.append((nx, ny))
                            
                            remaining_mines = num - flagged_count
                            
                            if len(hidden_neighbors) == remaining_mines and remaining_mines > 0:
                                for mine_pos in hidden_neighbors:
                                    if mine_pos not in definite_mines:
                                        definite_mines.append(mine_pos)
                    except Exception:
                        continue
                            
            return definite_mines
        except Exception as e:
            if self.debug_mode:
                print(f"Error buscando minas: {e}")
            return []

    def find_all_safe_moves(self):
        """Encuentra movimientos seguros con mejor validación"""
        safe_moves = []
        try:
            if not self.safe_board_access():
                return safe_moves
            
            cols, rows = self.get_board_dimensions()
            
            for x in range(cols):
                for y in range(rows):
                    try:
                        tile = self.game.board.board_list[x][y]
                        if tile.revealed and tile.type.isdigit():
                            num = int(tile.type)
                            neighbors = self.get_neighbors(x, y)
                            
                            flagged_count = 0
                            hidden_neighbors = []
                            
                            for nx, ny in neighbors:
                                neighbor_tile = self.game.board.board_list[nx][ny]
                                if neighbor_tile.flagged:
                                    flagged_count += 1
                                elif not neighbor_tile.revealed:
                                    hidden_neighbors.append((nx, ny))
                            
                            if flagged_count == num and hidden_neighbors:
                                for safe_pos in hidden_neighbors:
                                    if safe_pos not in safe_moves:
                                        safe_moves.append(safe_pos)
                    except Exception:
                        continue
                            
            return safe_moves
        except Exception as e:
            if self.debug_mode:
                print(f"Error buscando movimientos seguros: {e}")
            return []

    def analyze_board(self):
        """Análisis del tablero con manejo de errores"""
        if not self.debug_mode:
            return
            
        try:
            if not self.safe_board_access():
                print("❌ No se puede acceder al tablero")
                return
                
            cols, rows = self.get_board_dimensions()
            revealed = flagged = hidden = 0
            
            for x in range(cols):
                for y in range(rows):
                    tile = self.game.board.board_list[x][y]
                    if tile.revealed:
                        revealed += 1
                    elif tile.flagged:
                        flagged += 1
                    else:
                        hidden += 1
            
            print(f"📊 Reveladas: {revealed}, Banderas: {flagged}, Ocultas: {hidden}")
            
        except Exception as e:
            print(f"Error en análisis: {e}")

    # ==================== MÉTODOS DE ENTRENAMIENTO ====================

    def manual_training(self, iterations=50):
        """Entrenamiento manual con validaciones robustas"""
        print(f"\n🎓 ENTRENAMIENTO MANUAL INICIADO ({iterations} iteraciones)")
        
        # Validaciones previas
        if not self.training_enabled:
            print("❌ Entrenamiento deshabilitado")
            return False
            
        if len(self.memory) < self.batch_size:
            print(f"❌ Memoria insuficiente. Necesitas {self.batch_size}, tienes {len(self.memory)}")
            print("💡 Juega algunos juegos primero para acumular experiencias")
            return False
            
        if self.model is None:
            print("❌ Modelo no inicializado. Intenta reiniciar el juego.")
            return False
        
        # Pausar IA durante entrenamiento
        old_paused = self.paused
        self.paused = True
        
        try:
            total_loss = 0
            successful_iterations = 0
            
            for i in range(iterations):
                try:
                    loss = self.replay()
                    if loss is not None and not np.isnan(loss) and not np.isinf(loss):
                        total_loss += loss
                        successful_iterations += 1
                        
                    if (i + 1) % 10 == 0:
                        print(f"   Progreso: {i+1}/{iterations} (exitosas: {successful_iterations})")
                        
                except Exception as e:
                    if self.debug_mode:
                        print(f"   Error en iteración {i}: {e}")
            
            if successful_iterations > 0:
                avg_loss = total_loss / successful_iterations
                print(f"✅ ENTRENAMIENTO COMPLETADO")
                print(f"   📉 Loss promedio: {avg_loss:.4f}")
                print(f"   ✅ Iteraciones exitosas: {successful_iterations}/{iterations}")
                print(f"   🧠 Epsilon: {self.epsilon:.3f}")
                
                # Guardar después del entrenamiento
                self.save_state()
                return True
            else:
                print("❌ ENTRENAMIENTO FALLÓ - Ninguna iteración exitosa")
                return False
                
        except Exception as e:
            print(f"❌ Error crítico en entrenamiento: {e}")
            return False
        finally:
            # Restaurar estado
            self.paused = old_paused

    def replay(self):
        """Entrenamiento mejorado con mejor validación"""
        try:
            if len(self.memory) < self.batch_size or self.model is None:
                return None
                
            # Seleccionar batch válido
            batch_size = min(self.batch_size, len(self.memory))
            memory_list = list(self.memory)
            
            # Filtrar experiencias válidas
            valid_memories = []
            for exp in memory_list:
                if (len(exp) == 5 and 
                    exp[0] is not None and exp[3] is not None and
                    isinstance(exp[1], (int, np.integer)) and
                    isinstance(exp[2], (int, float, np.number))):
                    valid_memories.append(exp)
            
            if len(valid_memories) < batch_size:
                if self.debug_mode:
                    print(f"Experiencias válidas insuficientes: {len(valid_memories)}")
                return None
            
            minibatch = random.sample(valid_memories, batch_size)
            
            # Preparar datos
            states = np.array([x[0] for x in minibatch], dtype=np.float32)
            next_states = np.array([x[3] for x in minibatch], dtype=np.float32)
            
            # Verificar dimensiones
            if states.shape[0] != batch_size or next_states.shape[0] != batch_size:
                if self.debug_mode:
                    print("Error en dimensiones del batch")
                return None
            
            # Predicciones
            current_q_list = self.model.predict(states, verbose=0)
            future_q_list = self.model.predict(next_states, verbose=0)
            
            # Actualizar Q-values
            for i, (state, action, reward, next_state, done) in enumerate(minibatch):
                if action < len(current_q_list[i]):
                    if done:
                        current_q_list[i][action] = reward
                    else:
                        max_future_q = np.max(future_q_list[i])
                        current_q_list[i][action] = reward + self.gamma * max_future_q
            
            # Entrenar
            history = self.model.fit(
                states, 
                current_q_list, 
                batch_size=batch_size,
                epochs=1, 
                verbose=0
            )
            
            loss = history.history['loss'][0]
            
            # Actualizar epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
                
            return loss
            
        except Exception as e:
            if self.debug_mode:
                print(f"Error en replay: {e}")
            return None

    # ==================== MÉTODOS DE CONTROL ====================

    def force_save(self):
        """Guardado forzado"""
        print("\n🔄 GUARDADO MANUAL INICIADO...")
        self.save_state()

    def toggle_debug(self):
        """Toggle modo debug"""
        self.debug_mode = not self.debug_mode
        print(f"\n🔧 DEBUG MODE: {'ON' if self.debug_mode else 'OFF'}")

    def toggle_pause(self):
        """Pausar/reanudar IA"""
        self.paused = not self.paused
        status = "PAUSADA" if self.paused else "ACTIVA"
        print(f"\n⏯️ IA {status}")

    def set_speed(self, speed):
        """Cambiar velocidad"""
        speeds = {
            'very_slow': 3.0,
            'slow': 1.5, 
            'normal': 0.8,
            'fast': 0.3,
            'very_fast': 0.1
        }
        
        if speed in speeds:
            self.move_delay = speeds[speed]
            print(f"\n⏱️ Velocidad: {speed} ({self.move_delay}s entre movimientos)")
        else:
            print(f"\n❌ Velocidad inválida. Opciones: {list(speeds.keys())}")

    def show_stats(self):
        """Mostrar estadísticas detalladas"""
        print(f"\n📊 ESTADÍSTICAS DETALLADAS")
        print(f"{'='*50}")
        print(f"🎮 Juegos totales: {self.games_played}")
        print(f"🏆 Victorias: {self.wins}")
        print(f"💥 Derrotas: {self.losses}")
        
        if self.games_played > 0:
            win_rate = (self.wins / self.games_played) * 100
            print(f"📈 Tasa de victoria: {win_rate:.1f}%")
            
        if self.flags_placed > 0:
            flag_accuracy = (self.correct_flags / self.flags_placed) * 100
            print(f"✅ Banderas correctas: {self.correct_flags}")
            print(f"📊 Precisión banderas: {flag_accuracy:.1f}%")
            
        print(f"💥 Minas pisadas: {self.mines_hit}")
        print(f"🧠 Epsilon actual: {self.epsilon:.3f}")
        print(f"📚 Experiencias: {len(self.memory)}")
        print(f"🤖 Modelo: {'✅ Cargado' if self.model else '❌ Sin modelo'}")
        print(f"{'='*50}")

    # ==================== MÉTODOS AUXILIARES ====================

    def make_smart_random_move(self):
        """Movimiento aleatorio inteligente con validación"""
        try:
            if not self.safe_board_access():
                return None
                
            cols, rows = self.get_board_dimensions()
            candidates = []
            
            for x in range(cols):
                for y in range(rows):
                    tile = self.game.board.board_list[x][y]
                    if not tile.revealed and not tile.flagged:
                        # Priorizar celdas centrales
                        priority = 1
                        if 2 <= x <= cols-3 and 2 <= y <= rows-3:
                            priority = 3
                        elif not (x == 0 or x == cols-1 or y == 0 or y == rows-1):
                            priority = 2
                            
                        candidates.extend([(x, y)] * priority)
            
            return random.choice(candidates) if candidates else None
            
        except Exception as e:
            if self.debug_mode:
                print(f"Error en movimiento aleatorio: {e}")
            return None

    def calculate_reward(self):
        """Sistema de recompensas balanceado"""
        try:
            if not self.game.game_active:
                if hasattr(self.game, 'win') and self.game.win:
                    return 50.0  # Victoria
                else:
                    self.mines_hit += 1
                    return -50.0  # Derrota
            
            # Recompensas durante el juego
            reward = 0.0
            
            if self.safe_board_access():
                cols, rows = self.get_board_dimensions()
                revealed_count = sum(1 for x in range(cols) for y in range(rows) 
                                   if self.game.board.board_list[x][y].revealed)
                reward += revealed_count * 0.05  # Progreso
                
                # Penalización por banderas incorrectas
                if hasattr(self.game, 'flags_remaining') and self.game.flags_remaining < 0:
                    reward -= abs(self.game.flags_remaining) * 2
                    
            return reward
        except Exception as e:
            if self.debug_mode:
                print(f"Error calculando recompensa: {e}")
            return 0.0

    def position_to_action(self, x, y):
        """Convierte posición a acción con validación"""
        try:
            _, rows = self.get_board_dimensions()
            if rows > 0:
                return x * rows + y
            return 0
        except:
            return 0

    def action_to_position(self, action):
        """Convierte acción a posición con validación"""
        try:
            _, rows = self.get_board_dimensions()
            if rows > 0:
                return action // rows, action % rows
            return 0, 0
        except:
            return 0, 0

    def process_game_end(self):
        """Procesa el final del juego con mejor manejo"""
        try:
            if self.last_state is not None and self.last_action is not None:
                reward = self.calculate_reward()
                current_state = self.board_to_state()
                if current_state is not None:
                    self.remember(self.last_state, self.last_action, reward, current_state, True)
                
                # Actualizar estadísticas
                self.games_played += 1
                if hasattr(self.game, 'win') and self.game.win:
                    self.wins += 1
                    if self.debug_mode:
                        print("🏆 VICTORIA!")
                else:
                    self.losses += 1
                    if self.debug_mode:
                        print("💥 DERROTA")
                
                # Entrenamiento automático (más conservador)
                if (self.training_enabled and 
                    len(self.memory) >= self.batch_size and 
                    self.games_played % 3 == 0):  # Cada 3 juegos
                    try:
                        loss = self.replay()
                        if loss and self.debug_mode:
                            print(f"📚 Entrenamiento automático - Loss: {loss:.4f}")
                    except Exception as e:
                        if self.debug_mode:
                            print(f"Error en entrenamiento automático: {e}")
                
                # Guardar progreso cada 5 juegos
                if self.games_played % 5 == 0:
                    self.save_state()
                
                # Reiniciar variables
                self.reset_for_new_game()
        except Exception as e:
            print(f"Error procesando fin de juego: {e}")
            self.reset_for_new_game()

    def board_to_state(self):
        """Convierte tablero a estado con validación robusta"""
        try:
            if not self.safe_board_access():
                return None
                
            state = []
            cols, rows = self.get_board_dimensions()
            
            for x in range(cols):
                for y in range(rows):
                    try:
                        tile = self.game.board.board_list[x][y]
                        
                        revealed = 1.0 if tile.revealed else 0.0
                        flagged = 1.0 if tile.flagged else 0.0
                        
                        if tile.revealed and hasattr(tile, 'type') and tile.type.isdigit():
                            number = float(tile.type) / 8.0  # Normalizar 0-8
                        else:
                            number = 0.0
                        
                        state.extend([revealed, flagged, number])
                    except Exception:
                        # En caso de error, usar valores seguros
                        state.extend([0.0, 0.0, 0.0])
                        
            return np.array(state, dtype=np.float32)
        except Exception as e:
            if self.debug_mode:
                print(f"Error creando estado: {e}")
            return None

    def get_valid_actions(self):
        """Obtener acciones válidas con validación"""
        try:
            if not self.safe_board_access():
                return []
                
            valid_actions = []
            cols, rows = self.get_board_dimensions()
            
            for x in range(cols):
                for y in range(rows):
                    try:
                        tile = self.game.board.board_list[x][y]
                        if not tile.revealed and not tile.flagged:
                            valid_actions.append(self.position_to_action(x, y))
                    except Exception:
                        continue
                        
            return valid_actions
        except Exception as e:
            if self.debug_mode:
                print(f"Error obteniendo acciones válidas: {e}")
            return []

    def get_neighbors(self, x, y):
        """Obtiene vecinos con validación"""
        try:
            neighbors = []
            directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
            cols, rows = self.get_board_dimensions()
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < cols and 0 <= ny < rows:
                    neighbors.append((nx, ny))
            return neighbors
        except Exception as e:
            if self.debug_mode:
                print(f"Error obteniendo vecinos: {e}")
            return []

    def remember(self, state, action, reward, next_state, done):
        """Guarda experiencia con validación"""
        try:
            if (state is not None and next_state is not None and
                isinstance(action, (int, np.integer)) and
                isinstance(reward, (int, float, np.number)) and
                isinstance(done, bool)):
                self.memory.append((state.copy(), int(action), float(reward), next_state.copy(), done))
        except Exception as e:
            if self.debug_mode:
                print(f"Error guardando experiencia: {e}")

    def reset_for_new_game(self):
        """Reinicia variables para nuevo juego"""
        try:
            self.first_move = True
            self.last_state = None
            self.last_action = None
            self.move_count = 0
        except Exception as e:
            if self.debug_mode:
                print(f"Error reiniciando para nuevo juego: {e}")

    # ==================== MÉTODOS DE UTILIDAD ====================

    def get_model_info(self):
        """Información del modelo"""
        if self.model is None:
            return "Sin modelo"
        try:
            return f"Modelo cargado - Parámetros: {self.model.count_params()}"
        except:
            return "Modelo cargado - Info no disponible"

    def cleanup_memory(self):
        """Limpia memoria duplicada o corrupta"""
        try:
            original_size = len(self.memory)
            clean_memory = []
            
            for exp in list(self.memory):
                if (len(exp) == 5 and 
                    exp[0] is not None and exp[3] is not None):
                    clean_memory.append(exp)
            
            self.memory = deque(clean_memory, maxlen=5000)
            cleaned = original_size - len(self.memory)
            
            if cleaned > 0:
                print(f"🧹 Memoria limpiada: {cleaned} experiencias inválidas eliminadas")
                
        except Exception as e:
            print(f"Error limpiando memoria: {e}")

    def emergency_reset(self):
        """Reset de emergencia"""
        try:
            print("🚨 RESET DE EMERGENCIA")
            self.paused = False
            self.first_move = True
            self.last_state = None
            self.last_action = None
            self.move_count = 0
            
            # Intentar guardar antes del reset
            self.save_state()
            print("✅ Reset completado")
            
        except Exception as e:
            print(f"Error en reset de emergencia: {e}")