#main.py
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Desactiva el mensaje de bienvenida

import pygame
from settings import *
from sprites import *

class TileAnalyzer:
    @staticmethod
    def rgb_to_hex(rgb):
        """Convierte color RGB a hexadecimal"""
        return '#{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])
    
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convierte color hexadecimal a RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def analyze_face_state(screen):
        """Analiza el estado de la carita del juego con mayor precisión"""
        try:
            # Calcular posición absoluta de la carita
            face_x = WIDTH // 2 - 12
            face_y = (TOP_PANEL_HEIGHT // 2) - 12
            
            # Coordenadas absolutas de los píxeles a analizar
            pixel1_pos = (face_x + 8, face_y + 12)
            pixel2_pos = (face_x + 9, face_y + 10)
            
            # Obtener los píxeles
            pixel_8_12 = screen.get_at(pixel1_pos)
            pixel_9_10 = screen.get_at(pixel2_pos)
            
            # Convertir a hexadecimal
            hex_8_12 = TileAnalyzer.rgb_to_hex(pixel_8_12)
            hex_9_10 = TileAnalyzer.rgb_to_hex(pixel_9_10)
            
            # Umbrales de color más flexibles
            def is_yellow(pixel):
                return pixel[0] > 200 and pixel[1] > 200 and pixel[2] < 50  # R+G alto, B bajo
                
            def is_black(pixel):
                return pixel[0] < 50 and pixel[1] < 50 and pixel[2] < 50
            
            # Determinar el estado con tolerancia
            if is_yellow(pixel_8_12) and is_black(pixel_9_10):
                state = "Sonriendo"
            elif is_yellow(pixel_8_12) and is_yellow(pixel_9_10):
                state = "Triste (Perdido)"
            elif is_black(pixel_8_12) and is_black(pixel_9_10):
                state = "Con lentes (Ganado)"
            else:
                state = f"Desconocido (8,12: {hex_8_12}, 9,10: {hex_9_10})"
            
            #print(f"Estado detectado: {state}")
            #print("------------------------")
            
            return state, hex_8_12, hex_9_10
                
        except Exception as e:
            print(f"\nError analizando carita: {str(e)}")
            return "Error", "N/A", "N/A"

    @staticmethod
    def analyze_tile(screen, x, y):
        """Analiza una casilla en las coordenadas (x, y) y devuelve su tipo"""
        screen_x = x * TILESIZE
        screen_y = y * TILESIZE + TOP_PANEL_HEIGHT
        
        try:
            # Obtener píxeles y sus valores hexadecimales
            pixel_00 = screen.get_at((screen_x, screen_y))
            hex_00 = TileAnalyzer.rgb_to_hex(pixel_00)
            pixel_01 = screen.get_at((screen_x, screen_y + 1))
            hex_01 = TileAnalyzer.rgb_to_hex(pixel_01)
            center_pixel1 = screen.get_at((screen_x + 7, screen_y + 7))
            hex_center1 = TileAnalyzer.rgb_to_hex(center_pixel1)
            center_pixel2 = screen.get_at((screen_x + 8, screen_y + 8))
            hex_center2 = TileAnalyzer.rgb_to_hex(center_pixel2)
        except:
            return "Fuera de límites", {}, {}
        
        def color_match(c1, c2_hex, tolerance=10):
            c2_rgb = TileAnalyzer.hex_to_rgb(c2_hex)
            return all(abs(c1[i] - c2_rgb[i]) <= tolerance for i in range(3))
        
        # Diccionario con los colores detectados
        detected_colors = {
            'pixel_00': hex_00,
            'pixel_01': hex_01,
            'center_pixel1': hex_center1,
            'center_pixel2': hex_center2
        }
        
        # Verificar si la casilla está revelada o no
        if color_match(pixel_00, 'FFFFFF') and color_match(pixel_01, 'FFFFFF'):
            if color_match(center_pixel2, '000000'):
                return "Bandera", detected_colors, {'pixels_00_01': 'FFFFFF', 'centro': '000000'}
            return "Sin revelar", detected_colors, {'pixels_00_01': 'FFFFFF', 'centro': 'Otro'}
        elif color_match(pixel_00, '808080') and color_match(pixel_01, '808080'):
            if color_match(center_pixel2, '0000FF'):
                return "Número 1", detected_colors, {'pixels_00_01': '808080', 'centro': '0000FF'}
            elif color_match(center_pixel2, '008000'):
                return "Número 2", detected_colors, {'pixels_00_01': '808080', 'centro': '008000'}
            elif color_match(center_pixel2, 'FF0000'):
                return "Número 3", detected_colors, {'pixels_00_01': '808080', 'centro': 'FF0000'}
            elif color_match(center_pixel2, '000080'):
                return "Número 4", detected_colors, {'pixels_00_01': '808080', 'centro': '000080'}
            elif color_match(center_pixel2, '800000'):
                return "Número 5", detected_colors, {'pixels_00_01': '808080', 'centro': '800000'}
            elif color_match(center_pixel2, '008080'):
                return "Número 6", detected_colors, {'pixels_00_01': '808080', 'centro': '008080'}
            elif color_match(center_pixel2, '000000'):
                return "Número 7", detected_colors, {'pixels_00_01': '808080', 'centro': '000000'}
            elif color_match(center_pixel2, '808080'):
                return "Número 8", detected_colors, {'pixels_00_01': '808080', 'centro': '808080'}
            elif color_match(center_pixel2, 'C0C0C0'):
                return "Espacio vacío", detected_colors, {'pixels_00_01': '808080', 'centro': 'C0C0C0'}
        
        return "Desconocido", detected_colors, {}

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

game = Game()
while True:
    game.new()
    game.run()