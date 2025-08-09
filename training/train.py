import sys
import os

# Añadir el directorio padre al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tensorflow as tf  # Import principal recomendado
import numpy as np
from settings import ROWS, COLS

# Preprocesamiento del Estado del Tablero
def board_to_state(screen, analyzer):
    state = np.zeros((ROWS, COLS, 6), dtype=np.float32)
    
    # Analizar estado de la carita
    face_state, _, _ = analyzer.analyze_face_state(screen)
    game_active = 1.0 if "Sonriendo" in face_state else 0.0
    
    for x in range(ROWS):
        for y in range(COLS):
            tile_type, colors, _ = analyzer.analyze_tile(screen, x, y)
            
            # Características de la casilla
            features = [
                1.0 if tile_type == "Sin revelar" else 0.0,
                1.0 if tile_type == "Bandera" else 0.0,
                1.0 if "Número" in tile_type else 0.0,
                1.0 if tile_type == "Espacio vacío" else 0.0,
                float(tile_type.split()[-1]) / 8.0 if "Número" in tile_type else 0.0,
                game_active
            ]
            
            state[x, y] = features
    
    return state

# Arquitectura de la Red Neuronal
def create_model(rows, cols):
    input_layer = tf.keras.layers.Input(shape=(rows, cols, 6))
    
    # Capas convolucionales
    conv1 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_layer)
    conv2 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(conv1)
    
    # Capas para predicción de acciones
    flat = tf.keras.layers.Flatten()(conv2)
    dense1 = tf.keras.layers.Dense(128, activation='relu')(flat)
    
    # Dos salidas: clic izquierdo y derecho
    left_click = tf.keras.layers.Dense(rows * cols, activation='sigmoid', name='left')(dense1)
    right_click = tf.keras.layers.Dense(rows * cols, activation='sigmoid', name='right')(dense1)
    
    return tf.keras.models.Model(inputs=input_layer, outputs=[left_click, right_click])

def main():
    print("🔷 Iniciando entrenamiento...")
    model = create_model(ROWS, COLS)
    
    # Compila el modelo (esto evita la advertencia)
    model.compile(optimizer='adam',
                 loss={'left': 'binary_crossentropy', 
                       'right': 'binary_crossentropy'})
    
    model_path = os.path.join('models', 'minesweeper_model.h5')
    os.makedirs('models', exist_ok=True)
    model.save(model_path)
    print(f"✅ Modelo guardado en {model_path}")