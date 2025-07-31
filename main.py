import pygame
from settings import *
from sprites import *

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.TIMER_EVENT = pygame.USEREVENT + 1  # Evento específico para el temporizador
        self.reset_game()
        
    def reset_game(self):
        self.game_active = True
        self.first_click = True
        self.flags_remaining = AMOUNT_MINES
        self.elapsed_time = -1
        self.timer_started = False
        self.board = Board()
        self.board.display_board()
        
        # Initialize top panel elements
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
        
        # Set up timer event
        pygame.time.set_timer(self.TIMER_EVENT, 1000)  # 1 second interval

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
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()
        else:
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
        self.game_active = False
        self.timer_started = False
        self.playing = False
        self.win = won
        
        if won:
            self.face_button.change_state('win')
        else:
            self.face_button.change_state('loose')
            # Mostrar todas las minas y banderas incorrectas
            for row in self.board.board_list:
                for tile in row:
                    if tile.type == "X" and not tile.flagged:
                        tile.revealed = True
                    elif tile.flagged and tile.type != "X":
                        tile.revealed = True
                        # Asegurarse de asignar la imagen correcta
                        tile.image = tile_not_mine  # Esta línea ya está presente

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
                
            # CORREGIDO: Usar el evento específico TIMER_EVENT
            if event.type == self.TIMER_EVENT and self.timer_started and self.game_active:
                if self.elapsed_time < 999:
                    self.elapsed_time += 1
                    self.update_timer()
                else:
                    # Time's up - game over
                    self.end_game(False)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                # Check if face button was clicked
                if self.face_button.rect.collidepoint(mx, my):
                    self.new()
                    return
                    
                # Only process board clicks if game is active
                if not self.game_active:
                    continue
                    
                # Adjust for top panel
                if my < TOP_PANEL_HEIGHT:
                    continue
                    
                mx //= TILESIZE
                my = (my - TOP_PANEL_HEIGHT) // TILESIZE

                if event.button == 1:  # Left click
                    if not self.board.board_list[mx][my].flagged:
                        # Start timer on first click
                        if self.first_click:
                            self.first_click = False
                            self.timer_started = True
                            self.elapsed_time = 0
                            self.update_timer()
                            
                        # dig and check if exploded
                        if not self.board.dig(mx, my):
                            self.end_game(False)  # Game over
                        elif self.check_win():
                            self.end_game(True)  # Win

                if event.button == 3:  # Right click
                    if not self.board.board_list[mx][my].revealed:
                        # Toggle flag
                        self.board.board_list[mx][my].flagged = not self.board.board_list[mx][my].flagged
                        if self.board.board_list[mx][my].flagged:
                            self.flags_remaining -= 1
                        else:
                            self.flags_remaining += 1
                        self.update_flag_counter()

    def end_screen(self):
        # Wait for click to restart
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
        self.new()  # Start new game


game = Game()
while True:
    game.new()
    game.run()