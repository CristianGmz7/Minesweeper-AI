import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from game.game import Game
from ai.model import board_to_state
from ai.data_collector import DataCollector
from settings import TOP_PANEL_HEIGHT, TILESIZE, ROWS, COLS, AMOUNT_MINES

class TrainingGame(Game):
    def __init__(self, collector=None):
        self.first_click = True
        self.timer_started = False
        self.elapsed_time = 0
        self.flags_remaining = AMOUNT_MINES
        self.game_active = True
        self.playing = True
        
        # Ahora llama al constructor padre
        super().__init__()
        
        # Inicializa los componentes específicos
        self.collector = collector if collector else DataCollector()
        self.last_state = None
        self.games_completed = 0
        self.manual_mode = True
        
        # Configuración de pygame.mouse
        pygame.mouse.set_visible(True)
        self.last_mouse_pos = (0, 0)
        
    def events(self):
        """Manejo de eventos con recolección de datos"""
        for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.playing = False
                        if self.collector:
                            self.collector.save_data()
                        
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            self.playing = False
                            if self.collector:
                                self.collector.save_data()
                        elif event.key == pygame.K_s:
                            if self.collector:
                                self.collector.save_data()
                                print("💾 Datos guardados manualmente")
                        
                    if event.type == pygame.MOUSEBUTTONDOWN and self.game_active:
                        # Obtener posición actual del mouse
                        mouse_pos = pygame.mouse.get_pos()
                        self.last_mouse_pos = mouse_pos
                        
                        # Analizar pantalla para determinar acción
                        self._process_mouse_action(event.button, mouse_pos)
                    
                    # Manejo del temporizador
                    if event.type == self.TIMER_EVENT and self.timer_started and self.game_active:
                        if self.elapsed_time < 999:
                            self.elapsed_time += 1
                            self.update_timer()
                        else:
                            self.end_game(False)

    def _process_mouse_action(self, button, mouse_pos):
        """Procesa la acción del mouse basada en análisis de pantalla"""
        mx, my = mouse_pos
        
        # Verificar clic en la cara
        face_rect = getattr(self.face_button, 'rect', None)
        if face_rect and face_rect.collidepoint(mx, my):
            self.reset_game()
            return
        
        # Verificar clic fuera del tablero
        if my < TOP_PANEL_HEIGHT:
            return
        
        # Calcular coordenadas del tile
        tile_col = mx // TILESIZE
        tile_row = (my - TOP_PANEL_HEIGHT) // TILESIZE
        
        # Verificar límites
        if not (0 <= tile_col < COLS and 0 <= tile_row < ROWS):
            return
        
        # Capturar estado ANTES del clic
        if self.collector:
            self.last_state = board_to_state(self.screen, self.tile_analyzer)
        
        # Determinar tipo de acción basado en análisis visual
        tile_type, _, _ = self.tile_analyzer.analyze_tile(self.screen, tile_col, tile_row)
        
        # Procesar clic izquierdo (reveal)
        if button == 1 and "Sin revelar" in tile_type and "Bandera" not in tile_type:
            self._register_and_execute_action('left', tile_row, tile_col)
        
        # Procesar clic derecho (flag)
        elif button == 3 and "Sin revelar" in tile_type:
            self._register_and_execute_action('right', tile_row, tile_col)

    def _register_and_execute_action(self, action_type, row, col):
        """Registra y ejecuta una acción validada"""
        if self.collector and self.last_state is not None:
            self.collector.add_sample(self.last_state, action_type, row, col)
            print(f"📊 Acción registrada: {action_type.upper()} en ({row},{col})")
        
        # Ejecutar acción en el juego
        if action_type == 'left':
            self._execute_left_click(col, row)
        elif action_type == 'right':
            self._execute_right_click(col, row)

    def _execute_left_click(self, col, row):
        """Ejecuta un clic izquierdo validado"""
        if self.first_click:
            self.first_click = False
            self.timer_started = True
            self.elapsed_time = 0
            self.update_timer()
        
        if not self.board.dig(col, row):
            # 💀 Perdiste, guardar y reiniciar
            print("💀 Juego perdido, guardando muestras...")
            if self.collector:
                self.collector.save_data()
            self.games_completed += 1
            self.reset_game()
        elif self.check_win():
            self.games_completed += 1
            self.reset_game()

    def _execute_right_click(self, col, row):
        """Ejecuta un clic derecho validado"""
        tile = self.board.board_list[col][row]
        if tile.flagged:
            tile.flagged = False
            self.flags_remaining += 1
        else:
            if self.flags_remaining > 0:
                tile.flagged = True
                self.flags_remaining -= 1
        self.update_flag_counter()

    
    def reset_game(self):
        """Reinicia el juego y cuenta partidas completadas"""
        collector = getattr(self, 'collector', None)
        games_completed = getattr(self, 'games_completed', 0)
        
        # Reiniciar juego padre
        super().reset_game()
        
        # Restaurar estado del entrenamiento
        self.collector = collector
        self.games_completed = games_completed
        
        # Actualizar contador si no era primer clic
        if not self.first_click:
            self.games_completed += 1
            print(f"🎮 Partidas completadas: {self.games_completed}")
    
    def run_training_session(self, target_games=50):
        """
        Ejecuta una sesión de entrenamiento
        
        Args:
            target_games: Número objetivo de partidas
        """
        print("🎯 Sesión de entrenamiento iniciada")
        print("=" * 40)
        print("Controles:")
        print("• Clic izquierdo: revelar casilla")
        print("• Clic derecho: colocar/quitar bandera")
        print("• R: reiniciar partida")
        print("• S: guardar datos")
        print("• ESC: salir y guardar")
        print(f"• Meta: {target_games} partidas")
        print("=" * 40)
        
        clock = pygame.time.Clock()
        
        try:
            while self.games_completed < target_games:
                self.events()
                
                # Mostrar progreso cada 10 partidas
                if self.games_completed > 0 and self.games_completed % 10 == 0:
                    remaining = target_games - self.games_completed
                    print(f"📈 Progreso: {self.games_completed}/{target_games} ({remaining} restantes)")
                    
                    # Guardar progreso automáticamente
                    if self.collector:
                        self.collector.save_data()
                
                self.draw()
                pygame.display.flip()
                clock.tick(60)
                
                # Salir si se cerró la ventana
                if not self.playing:
                    break
            
            print(f"✅ Sesión completada: {self.games_completed} partidas")
            if self.collector:
                self.collector.save_data()
                print(f"📊 Total de muestras recolectadas: {self.collector.sample_count}")
                
        except KeyboardInterrupt:
            print("\n⚠️ Sesión interrumpida por el usuario")
            if self.collector:
                self.collector.save_data()
        
        return self.collector

def manual_data_collection():
    """Función para recolección manual de datos"""
    print("🎮 Iniciando recolección manual de datos")
    
    # Crear recolector
    collector = DataCollector()
    
    # Cargar datos existentes si los hay
    collector.load_data()
    
    # Crear juego de entrenamiento
    training_game = TrainingGame(collector)
    
    # Preguntar cuántas partidas quiere jugar el usuario
    try:
        target = int(input("¿Cuántas partidas quieres jugar? (recomendado: 30-50): "))
    except:
        target = 30
    
    # Ejecutar sesión
    final_collector = training_game.run_training_session(target)
    
    return final_collector

if __name__ == "__main__":
    manual_data_collection()