import pygame
import os
from game.game import Game
from ai.model import MinesweeperModel, board_to_state
from agents.ai_agent import AIAgent
from settings import TILESIZE, TOP_PANEL_HEIGHT, ROWS, COLS

class AIGame(Game):
    def __init__(self, model_path="models/minesweeper_model.h5"):
        self.ai_enabled = False
        self.ai_agent = None
        self.ai_delay = 1000
        self.last_ai_action = 0
        self.playing = True 

        super().__init__()
        
        # Cargar modelo de IA
        self.ai_model = MinesweeperModel()
        self.ai_agent = None
        
         # Configuración de IA
        if os.path.exists(model_path):
            self.ai_model = MinesweeperModel()
            if self.ai_model.load_model(model_path):
                self.ai_agent = AIAgent(self.ai_model)
                print("✅ IA cargada correctamente")
        
        # Configuración de IA
        self.ai_enabled = False
        self.ai_delay = 1000  # 1 segundo entre acciones de IA
        self.last_ai_action = 0
        self.manual_override = True  # Permitir control manual siempre
        
    def events(self):
        """Manejo de eventos con soporte para IA"""
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Activar/desactivar IA
                    if self.ai_agent:
                        self.ai_enabled = not self.ai_enabled
                        status = "ACTIVADA" if self.ai_enabled else "DESACTIVADA"
                        print(f"🤖 IA {status}")
                    else:
                        print("❌ No hay IA disponible")
                        
                elif event.key == pygame.K_r:
                    # Reiniciar juego
                    self.reset_game()
                    print("🔄 Juego reiniciado")
                    
                elif event.key == pygame.K_h:
                    # Mostrar ayuda
                    self.show_help()
                    
                elif event.key == pygame.K_ESCAPE:
                    self.playing = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Control manual siempre disponible
                self.handle_mouse_click(event)
        
        # Ejecutar acción de IA si está habilitada
        if (self.ai_enabled and self.ai_agent and self.game_active and 
            current_time - self.last_ai_action > self.ai_delay):
            self.execute_ai_action()
            self.last_ai_action = current_time
        
        # Llamar eventos del padre (timer, etc.)
        self.handle_timer_events()
    
    def handle_mouse_click(self, event):
        """Maneja clics del mouse"""
        mx, my = pygame.mouse.get_pos()
        
        # Click en cara para reiniciar
        if self.face_button.rect.collidepoint(mx, my):
            self.reset_game()
            return
        
        # Click fuera del área de juego
        if my < TOP_PANEL_HEIGHT:
            return
        
        # Calcular coordenadas de casilla
        tile_col = mx // TILESIZE
        tile_row = (my - TOP_PANEL_HEIGHT) // TILESIZE
        
        # Verificar límites
        if not (0 <= tile_col < COLS and 0 <= tile_row < ROWS):
            return
        
        if not self.game_active:
            return
        
        # Ejecutar acción
        if event.button == 1:  # Clic izquierdo
            self.execute_left_click(tile_col, tile_row)
        elif event.button == 3:  # Clic derecho
            self.execute_right_click(tile_col, tile_row)
    
    def execute_left_click(self, col, row):
        """Ejecuta clic izquierdo en la posición especificada"""
        tile = self.board.board_list[col][row]
        
        if tile.flagged:
            return  # No se puede revelar casilla con bandera
        
        # Primer clic - iniciar temporizador
        if self.first_click:
            self.first_click = False
            self.timer_started = True
            self.elapsed_time = 0
            self.update_timer()
        
        # Revelar casilla
        if not self.board.dig(col, row):
            self.reset_game()  # Perdió
            print(f"💥 Mina en ({row},{col}) - Juego perdido")
        elif self.check_win():
            self.reset_game()   # Ganó
            print("🎉 ¡Juego ganado!")
        else:
            print(f"🔍 Revelada casilla ({row},{col})")
    
    def execute_right_click(self, col, row):
        """Ejecuta clic derecho en la posición especificada"""
        tile = self.board.board_list[col][row]
        
        if tile.revealed:
            return  # No se puede marcar casilla revelada
        
        # Alternar bandera
        if tile.flagged:
            # Quitar bandera
            tile.flagged = False
            self.flags_remaining += 1
            print(f"🚩❌ Bandera quitada en ({row},{col})")
        else:
            # Colocar bandera (si hay disponibles)
            if self.flags_remaining > 0:
                tile.flagged = True
                self.flags_remaining -= 1
                print(f"🚩✅ Bandera colocada en ({row},{col})")
        
        self.update_flag_counter()
    
    def execute_ai_action(self):
        """Ejecuta una acción de la IA"""
        if not self.ai_agent:
            return
        
        # Obtener estado actual
        current_state = board_to_state(self.screen, self.tile_analyzer)
        
        # Predecir acción
        action = self.ai_agent.predict_action(current_state, self.flags_remaining)
        
        if action:
            action_type, row, col = action
            
            print(f"🤖 IA ejecuta {action_type.upper()} en ({row},{col})")
            
            if action_type == 'left':
                self.execute_left_click(col, row)
            elif action_type == 'right':
                self.execute_right_click(col, row)
        else:
            print("🤖 IA no encuentra acción válida")
            # Desactivar IA si no puede continuar
            self.ai_enabled = False
    
    def handle_timer_events(self):
        """Maneja eventos del temporizador"""
        for event in pygame.event.get():
            if event.type == self.TIMER_EVENT and self.timer_started and self.game_active:
                if self.elapsed_time < 999:
                    self.elapsed_time += 1
                    self.update_timer()
                else:
                    self.reset_game()
    
    def show_help(self):
        """Muestra ayuda en consola"""
        print("\n" + "="*50)
        print("🎮 CONTROLES DEL JUEGO")
        print("="*50)
        print("🖱️  Clic izquierdo     → Revelar casilla")
        print("🖱️  Clic derecho      → Colocar/quitar bandera")
        print("⌨️  ESPACIO           → Activar/desactivar IA")
        print("⌨️  R                 → Reiniciar juego")
        print("⌨️  H                 → Mostrar esta ayuda")
        print("⌨️  ESC               → Salir")
        print("="*50)
        print(f"🤖 IA: {'ACTIVADA' if self.ai_enabled else 'DESACTIVADA'}")
        print(f"🚩 Banderas restantes: {self.flags_remaining}")
        print("="*50 + "\n")
    
    def draw(self):
        """Dibuja el juego con información adicional"""
        super().draw()
        
        # Mostrar estado de IA en la ventana del juego
        if self.ai_agent:
            color = (0, 255, 0) if self.ai_enabled else (255, 0, 0)
            status_text = "IA ON" if self.ai_enabled else "IA OFF"
            # Aquí podrías añadir texto en la pantalla si quisieras
    
    def run(self):
        """Ejecuta el juego con IA"""
        print("🎯 Minesweeper con IA iniciado")
        self.show_help()
        
        # Bucle principal
        clock = pygame.time.Clock()
        
        while self.playing:
            self.events()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

def main():
    """Función principal"""
    print("🎮 Minesweeper IA")
    print("Iniciando juego...")
    
    # Verificar si existe modelo entrenado
    model_path = "models/minesweeper_model.h5"
    
    if not os.path.exists(model_path):
        print("⚠️ No se encontró modelo entrenado.")
        print("Opciones:")
        print("1. Jugar sin IA (solo manual)")
        print("2. Entrenar IA primero")
        
        choice = input("Selecciona opción (1-2): ").strip()
        
        if choice == '2':
            from ai.trainer import quick_train
            print("🤖 Iniciando entrenamiento rápido...")
            model = quick_train('mixed')
            if not model:
                print("❌ Error en entrenamiento. Jugando sin IA.")
    
      # Iniciar juego en modo manual si no hay IA
    if not os.path.exists(model_path):
        from game.game import Game  # Importa la clase base Game
        print("🚀 Iniciando juego en modo manual...")
        game = Game()  # Usa la clase base en lugar de AIGame
        game.run()
    else:
        game = AIGame(model_path)
        game.run()
        
if __name__ == "__main__":
    main()