import pygame
from settings import *
from sprites import *
from ia.Principiante import Beginner
from ia.Intermedio import Intermedio    
from ia.IAExperto import ExpertAI

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.TIMER_EVENT = pygame.USEREVENT + 1  # Evento específico para el temporizador
        self.reset_game()
        self.ai_mode = None  
        self.ai = None
    
    def set_ai_mode(self, mode):
        self.ai_mode = mode
        if mode == 'beginner':
            from ia.Principiante import Beginner
            self.ai = Beginner(self)
        elif mode == 'intermediate':
            from ia.Intermedio import Intermedio
            self.ai = Intermedio(self)
        elif mode == 'expert':
            # Importar tu nueva clase ExpertAI
            from ia.IAExperto import ExpertAI
            self.ai = ExpertAI(self)
            # Mostrar ayuda específica para IA experta
            print("\n💡 IA EXPERTA ACTIVADA - Controles disponibles:")
            print("   [T] - Entrenamiento manual")
            print("   [S] - Guardar progreso") 
            print("   [D] - Debug mode")
            print("   [P] - Pausar/reanudar")
            print("   [F1-F5] - Velocidades")
            print("   [H] - Ayuda completa")
        else:
            self.ai = None

    def reset_game(self):
        """Reiniciar juego MEJORADO"""
        # Notificar a IA sobre reinicio
        if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'reset_for_new_game'):
            try:
                self.ai.reset_for_new_game()
            except Exception as e:
                print(f"Error reiniciando IA: {e}")
        
        # Cancelar timer de auto-reinicio
        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
        
        # Reiniciar estado del juego
        self.game_active = True
        self.first_click = True
        self.flags_remaining = AMOUNT_MINES
        self.elapsed_time = -1
        self.timer_started = False
        self.board = Board()
        self.board.display_board()
        
        # Reinicializar elementos de UI
        self.flag_digits = [
            Digit(10, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2),
            Digit(10 + DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2),
            Digit(10 + 2 * DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2)
        ]
        self.update_flag_counter()
        
        self.face_button = FaceButton(WIDTH // 2, TOP_PANEL_HEIGHT // 2)
        
        self.timer_digits = [
            Digit(WIDTH - 10 - 3 * DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2),
            Digit(WIDTH - 10 - 2 * DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2),
            Digit(WIDTH - 10 - DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2)
        ]
        self.update_timer()
        
        # Reiniciar timer principal
        pygame.time.set_timer(self.TIMER_EVENT, 1000)

    def update_flag_counter(self):
        """CORREGIDO: Manejo correcto de números de 3 dígitos"""
        # Asegurarse de que el número está en el rango 0-999
        count = min(max(self.flags_remaining, 0), 999)
        
        # Convertir a string con 3 dígitos
        count_str = str(count).zfill(3)
        
        # Asignar cada dígito a su posición
        self.flag_digits[0].set_digit(count_str[0])
        self.flag_digits[1].set_digit(count_str[1])
        self.flag_digits[2].set_digit(count_str[2])

    def update_timer(self):
        """CORREGIDO: Manejo correcto del tiempo"""
        if self.elapsed_time < 0:
            for digit in self.timer_digits:
                digit.set_digit('minus')
        else:
            time = min(self.elapsed_time, 999)
            time_str = str(time).zfill(3)
            
            self.timer_digits[0].set_digit(time_str[0])
            self.timer_digits[1].set_digit(time_str[1])
            self.timer_digits[2].set_digit(time_str[2])

    def new(self):
        self.reset_game()

    def run(self):
        """Bucle principal OPTIMIZADO"""
        self.playing = True
        
        while self.playing:
            self.clock.tick(FPS)
            
            # Ejecutar IA si está activa
            if self.ai and self.game_active:
                try:
                    # Intentar movimiento de IA
                    move_made = self.ai.make_move()
                    
                    # Solo verificar condiciones si se hizo un movimiento
                    if move_made:
                        # Verificar victoria
                        if self.check_win():
                            self.end_game(True)
                        # La derrota se maneja automáticamente en board.dig()
                        
                except Exception as e:
                    print(f"❌ Error crítico en IA: {e}")
                    # En caso de error crítico, desactivar IA temporalmente
                    print("🔄 Desactivando IA por error crítico")
                    self.ai = None
                    self.ai_mode = None
                    
            # Procesar eventos
            self.events()
            
            # Dibujar
            self.draw()
        
        # Pantalla final
        self.end_screen()

    def draw(self):
        # Draw top panel
        top_panel = pygame.Surface((WIDTH, TOP_PANEL_HEIGHT))
        top_panel.fill(LIGHTGREY)
        self.screen.blit(top_panel, (0, 0))
        
        # Draw flag counter
        for digit in self.flag_digits:
            digit.draw(self.screen)
        
        # Draw face button
        self.face_button.draw(self.screen)
        
        # Draw timer
        for digit in self.timer_digits:
            digit.draw(self.screen)
        
        # Draw board
        self.board.draw(self.screen)
        
        pygame.display.flip()

    def check_win(self):
        for row in self.board.board_list:
            for tile in row:
                if tile.type != "X" and not tile.revealed:
                    return False
        return True

    def end_game(self, won):
        """Finalizar juego MEJORADO"""
        self.game_active = False
        self.timer_started = False
        self.win = won
        
        # Notificar a la IA ANTES de cambiar el estado
        if hasattr(self, 'ai') and self.ai:
            try:
                if hasattr(self.ai, 'process_game_end'):
                    self.ai.process_game_end()
            except Exception as e:
                print(f"Error procesando fin de juego: {e}")
        
        # Cambiar cara
        if won:
            self.face_button.change_state('win')
            print("🏆 ¡VICTORIA!")
        else:
            self.face_button.change_state('loose')
            print("💥 DERROTA")
            
            # Mostrar minas al perder
            for row in self.board.board_list:
                for tile in row:
                    if tile.type == "X" and not tile.flagged:
                        tile.revealed = True
                    elif tile.flagged and tile.type != "X":
                        tile.revealed = True

        # Auto-reinicio después de 3 segundos si hay IA activa
        if self.ai:
            pygame.time.set_timer(pygame.USEREVENT + 2, 3000)  # 3 segundos
        else:
            self.playing = False

    def events(self):
        """Manejo de eventos CORREGIDO"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Guardar antes de salir
                if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'save_state'):
                    print("💾 Guardando progreso antes de salir...")
                    self.ai.save_state()
                pygame.quit()
                quit(0)
                
            # Timer del juego
            if event.type == self.TIMER_EVENT and self.timer_started and self.game_active:
                if self.elapsed_time < 999:
                    self.elapsed_time += 1
                    self.update_timer()
                else:
                    self.end_game(False)

            # Clicks del mouse (jugador humano)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                # Click en cara para reiniciar
                if self.face_button.rect.collidepoint(mx, my):
                    self.new()
                    continue
                    
                # Solo procesar clicks si el juego está activo y no hay IA activa
                if event.type == pygame.MOUSEBUTTONDOWN and self.ai is None:
                    mx, my = pygame.mouse.get_pos()
                    
                # Ajustar coordenadas
                if my >= TOP_PANEL_HEIGHT and self.game_active:
                    mx //= TILESIZE
                    my = (my - TOP_PANEL_HEIGHT) // TILESIZE
                
                    try:
                        tile = self.board.board_list[mx][my]

                # Click izquierdo - cavar
                        if event.button == 1 and not tile.flagged:
                                if self.first_click:
                                    self.first_click = False
                                    self.timer_started = True
                                    self.elapsed_time = 0
                                    self.update_timer()
                                    
                                if not self.board.dig(mx, my):
                                    self.end_game(False)
                                elif self.check_win():
                                    self.end_game(True)
                # Click derecho - bandera
                        elif event.button == 3 and not tile.revealed:
                                        tile.flagged = not tile.flagged
                                        if tile.flagged:
                                            self.flags_remaining -= 1
                                        else:
                                            self.flags_remaining += 1
                                        self.update_flag_counter()
                                        
                    except IndexError:
                        pass    
    
            # CONTROLES DE TECLADO
            if event.type == pygame.KEYDOWN:
                self.handle_keyboard_input(event.key)

    def handle_keyboard_input(self, key):
        """Maneja entrada de teclado - MÉTODO SEPARADO PARA MEJOR ORGANIZACIÓN"""
        
        # ============= ACTIVAR IAs =============
        if key == pygame.K_0:
            # Desactivar IA
            self.ai_mode = None
            self.ai = None
            print("🚫 IA DESACTIVADA - Modo manual")
            
        elif key == pygame.K_1:
            self.set_ai_mode('beginner')
            print("🤖 IA PRINCIPIANTE activada")
            
        elif key == pygame.K_2:
            self.set_ai_mode('intermediate')
            print("🤖 IA INTERMEDIA activada")
            
        elif key == pygame.K_3:
            self.set_ai_mode('expert')
            print("🤖 IA EXPERTA activada")
            
        # ============= CONTROLES DE IA EXPERTA =============
        elif key == pygame.K_t:
            # ENTRENAMIENTO MANUAL INTENSIVO
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'manual_training'):
                print("\n🎓 INICIANDO ENTRENAMIENTO MANUAL...")
                self.ai.manual_training(50)
            else:
                print("❌ No hay IA Experta activa")
                
        elif key == pygame.K_r:
            # ENTRENAMIENTO RÁPIDO
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'replay'):
                print("🎓 Entrenamiento rápido...")
                loss = self.ai.replay()
                if loss:
                    print(f"   Loss: {loss:.4f}")
                else:
                    print("   Sin suficientes experiencias")
            else:
                print("❌ No hay IA Experta activa")
                
        elif key == pygame.K_s:
            # GUARDAR PROGRESO
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'force_save'):
                self.ai.force_save()
            elif hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'save_state'):
                self.ai.save_state()
            else:
                print("❌ No hay IA activa para guardar")
                
        # ============= CONTROLES DE DEBUG =============
        elif key == pygame.K_d:
            # TOGGLE DEBUG
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'toggle_debug'):
                self.ai.toggle_debug()
            else:
                print("❌ No hay IA activa")
                
        elif key == pygame.K_p:
            # PAUSAR/REANUDAR IA
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'toggle_pause'):
                self.ai.toggle_pause()
            else:
                print("❌ No hay IA activa")
                
        elif key == pygame.K_i:
            # MOSTRAR ESTADÍSTICAS
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'show_stats'):
                self.ai.show_stats()
            else:
                print("❌ No hay IA activa")
                
        # ============= CONTROLES DE VELOCIDAD =============
        elif key == pygame.K_F1:
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'set_speed'):
                self.ai.set_speed('very_slow')
            else:
                print("❌ No hay IA activa")
                
        elif key == pygame.K_F2:
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'set_speed'):
                self.ai.set_speed('slow')
            else:
                print("❌ No hay IA activa")
                
        elif key == pygame.K_F3:
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'set_speed'):
                self.ai.set_speed('normal')
            else:
                print("❌ No hay IA activa")
                
        elif key == pygame.K_F4:
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'set_speed'):
                self.ai.set_speed('fast')
            else:
                print("❌ No hay IA activa")
                
        elif key == pygame.K_F5:
            if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'set_speed'):
                self.ai.set_speed('very_fast')
            else:
                print("❌ No hay IA activa")
                
        # ============= AYUDA =============
        elif key == pygame.K_h:
            self.show_help()
            
        # ============= REINICIO RÁPIDO =============
        elif key == pygame.K_n:
            print("🔄 Nuevo juego")
            self.new()

    def show_help(self):
        """Muestra ayuda completa"""
        print("\n" + "="*70)
        print("🎮 MINESWEEPER IA - GUÍA COMPLETA DE CONTROLES")
        print("="*70)
        
        print("\n🤖 ACTIVAR/DESACTIVAR IA:")
        print("   [0] - Desactivar IA (modo manual)")
        print("   [1] - IA Principiante")
        print("   [2] - IA Intermedia")
        print("   [3] - IA Experta")
        
        print("\n🎓 ENTRENAMIENTO (solo IA Experta):")
        print("   [T] - Entrenamiento manual intensivo (50 iteraciones)")
        print("   [R] - Entrenamiento rápido (1 iteración)")
        print("   [S] - Guardar progreso manualmente")
        
        print("\n🔧 DEBUG Y CONTROL:")
        print("   [D] - Activar/desactivar modo debug")
        print("   [P] - Pausar/reanudar IA")
        print("   [I] - Mostrar estadísticas de IA")
        print("   [H] - Mostrar esta ayuda")
        
        print("\n⏱️ VELOCIDAD DE IA:")
        print("   [F1] - Muy lento (3.0s) - Para análisis detallado")
        print("   [F2] - Lento (1.5s)")
        print("   [F3] - Normal (0.8s)")
        print("   [F4] - Rápido (0.3s)")
        print("   [F5] - Muy rápido (0.1s) - Para entrenamiento masivo")
        
        print("\n🎮 JUEGO:")
        print("   [N] - Nuevo juego")
        print("   [Click cara] - Reiniciar")
        print("   [Click izq] - Cavar celda")
        print("   [Click der] - Colocar/quitar bandera")
        
        print("\n💡 CONSEJOS PARA ENTRENAR IA:")
        print("   1. Activa IA Experta: [3]")
        print("   2. Pon velocidad lenta: [F1]")
        print("   3. Activa debug: [D]")
        print("   4. Observa cómo juega")
        print("   5. Si comete errores: [T] para entrenamiento")
        print("   6. Guarda progreso: [S]")
        print("   7. Acelera cuando mejore: [F4] o [F5]")
        
        print("\n📊 PROGRESO:")
        print("   - El progreso se guarda automáticamente cada 5 juegos")
        print("   - Usa [I] para ver estadísticas detalladas")
        print("   - Los archivos se guardan como ai_model.keras, ai_memory.pkl, ai_stats.pkl")
        
        print("="*70)

    def end_screen(self):
        """Pantalla final mejorada"""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Guardar antes de salir
                    if hasattr(self, 'ai') and self.ai and hasattr(self.ai, 'save_state'):
                        print("💾 Guardando antes de salir...")
                        self.ai.save_state()
                    pygame.quit()
                    quit(0)
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    waiting = False
        
        self.new()


game = Game()
while True:
    game.new()
    game.run()