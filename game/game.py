import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Desactiva el mensaje de bienvenida

import pygame
from settings import WIDTH, HEIGHT, TITLE, AMOUNT_MINES, TOP_PANEL_HEIGHT, DIGIT_HEIGHT, DIGIT_WIDTH, FPS, LIGHTGREY, TILESIZE
from utils.tile_analyzer import TileAnalyzer
from game.board import Board
from game.sprites import Digit, FaceButton, tile_not_mine

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.TIMER_EVENT = pygame.USEREVENT + 1
        self.tile_analyzer = TileAnalyzer()
        self.reset_game()
        
    def reset_game(self):
        self.game_active = True
        self.first_click = True
        self.flags_remaining = AMOUNT_MINES
        self.elapsed_time = -1
        self.timer_started = False
        self.board = Board()
        #self.board.display_board()
        
        # Inicializar elementos del panel superior
        self.flag_digits = [
            Digit(10, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2),
            Digit(10 + DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2),
            Digit(10 + 2 * DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2)
        ]
        self.update_flag_counter()
        
        # Asegurar que la cara esté en estado "Sonriendo"
        self.face_button = FaceButton(WIDTH // 2, TOP_PANEL_HEIGHT // 2)
        self.face_button.change_state('normal')  # Forzar estado inicial
        
        self.timer_digits = [
            Digit(WIDTH - 10 - 3 * DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2),
            Digit(WIDTH - 10 - 2 * DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2),
            Digit(WIDTH - 10 - DIGIT_WIDTH, (TOP_PANEL_HEIGHT - DIGIT_HEIGHT) // 2)
        ]
        self.update_timer()
        
        pygame.time.set_timer(self.TIMER_EVENT, 1000)
        
        # Forzar actualización visual antes de la primera detección
        self.draw()
        pygame.display.flip()
        pygame.time.delay(50)  # Pequeña pausa
        
        # Mostrar estado inicial
        game_state, _, _ = self.tile_analyzer.analyze_face_state(self.screen)
        print(f"Estado inicial: {game_state}")

    def update_flag_counter(self):
        count = min(max(self.flags_remaining, 0), 999)
        count_str = str(count).zfill(3)
        self.flag_digits[0].set_digit(count_str[0])
        self.flag_digits[1].set_digit(count_str[1])
        self.flag_digits[2].set_digit(count_str[2])

    def update_timer(self):
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
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()
        else:
            self.end_screen()

    def draw(self):
        top_panel = pygame.Surface((WIDTH, TOP_PANEL_HEIGHT))
        top_panel.fill(LIGHTGREY)
        self.screen.blit(top_panel, (0, 0))
        
        for digit in self.flag_digits:
            digit.draw(self.screen)
        
        self.face_button.draw(self.screen)
        
        for digit in self.timer_digits:
            digit.draw(self.screen)
        
        self.board.draw(self.screen)
        
        pygame.display.flip()

    def check_win(self):
        for row in self.board.board_list:
            for tile in row:
                if tile.type != "X" and not tile.revealed:
                    return False
        return True

    def end_game(self, won):
        self.game_active = False
        self.timer_started = False
        self.playing = False
        
        if won:
            self.face_button.change_state('win')
            print("¡Juego ganado! Estado de la cara: Ganado")
        else:
            self.face_button.change_state('loose')
            print("¡Juego perdido! Estado de la cara: Perdido")
            
        # Mostrar minas y banderas incorrectas
        for row in self.board.board_list:
            for tile in row:
                if tile.type == "X" and not tile.flagged:
                    tile.revealed = True
                elif tile.flagged and tile.type != "X":
                    tile.revealed = True
                    tile.image = tile_not_mine

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
                
            if event.type == self.TIMER_EVENT and self.timer_started and self.game_active:
                if self.elapsed_time < 999:
                    self.elapsed_time += 1
                    self.update_timer()
                else:
                    self.end_game(False)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                if self.face_button.rect.collidepoint(mx, my):
                    self.new()
                    return
                    
                if not self.game_active:
                    continue
                    
                if my < TOP_PANEL_HEIGHT:
                    continue

                # Mostrar estado ANTES del clic (con depuración)
                game_state, _, _ = self.tile_analyzer.analyze_face_state(self.screen)
                    
                # Mostrar estado ANTES del clic
                game_state, color_8_12, color_16_12 = self.tile_analyzer.analyze_face_state(self.screen)
                print(f"Estado del juego: {'Sonriendo' if game_state == 'Jugando' else game_state}")
                
                tile_x = mx // TILESIZE
                tile_y = (my - TOP_PANEL_HEIGHT) // TILESIZE
                
                # Primera lectura - estado actual antes del clic
                tile_type1, colors1, _ = self.tile_analyzer.analyze_tile(self.screen, tile_x, tile_y)
                print(f"Pre-clic: {tile_type1}")
                
                # Procesar el clic
                clicked = False
                if event.button == 1:  # Left click
                    if not self.board.board_list[tile_x][tile_y].flagged:
                        if self.first_click:
                            self.first_click = False
                            self.timer_started = True
                            self.elapsed_time = 0
                            self.update_timer()
                            
                        if not self.board.dig(tile_x, tile_y):
                            self.end_game(False)
                            print("¡Perdido! Estado de la cara: Triste")
                        elif self.check_win():
                            self.end_game(True)
                            print("¡Ganado! Estado de la cara: Con lentes")
                        clicked = True

                if event.button == 3:  # Right click
                    if not self.board.board_list[tile_x][tile_y].revealed:
                        # Verificar si hay banderas disponibles O si ya hay una bandera en esta casilla (para permitir quitarla)
                        if self.flags_remaining > 0 or self.board.board_list[tile_x][tile_y].flagged:
                            self.board.board_list[tile_x][tile_y].flagged = not self.board.board_list[tile_x][tile_y].flagged
                            if self.board.board_list[tile_x][tile_y].flagged:
                                self.flags_remaining -= 1
                            else:
                                self.flags_remaining += 1
                            self.update_flag_counter()
                            clicked = True
                
                # Segunda lectura solo si se procesó un clic válido
                if clicked:
                    # Forzar actualización de la pantalla
                    self.draw()
                    pygame.display.flip()
                    
                    # Pequeña pausa para asegurar la actualización
                    pygame.time.delay(100)
                    
                    # Segunda lectura - estado después del clic
                    tile_type2, colors2, _ = self.tile_analyzer.analyze_tile(self.screen, tile_x, tile_y)
                    print(f"Post-clic: {tile_type2}")
                    
                    # Mostrar estado DESPUÉS del clic si el juego sigue activo
                    if self.game_active:
                        game_state, color_8_12, color_16_12 = self.tile_analyzer.analyze_face_state(self.screen)
                        #print(f"Estado del juego: {'Sonriendo' if game_state == 'Jugando' else game_state}")
                    
                    # Mostrar diferencias si las hay
                    #if tile_type1 != tile_type2:
                     #   print(">> Cambio detectado <<")
                
                #print("----------------------")

    def end_screen(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
        self.new()
