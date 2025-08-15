from settings import *

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
