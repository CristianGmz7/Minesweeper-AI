import tensorflow as tf
import numpy as np
from settings import ROWS, COLS

class MinesweeperModel:
    def __init__(self):
        self.model = None
        
    def create_model(self):
        """Crea el modelo de red neuronal"""
        # Input: estado del tablero (ROWS, COLS, 6 features)
        input_layer = tf.keras.layers.Input(shape=(ROWS, COLS, 6))
        
        # Capas convolucionales y de normalización
        x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_layer)
        x = tf.keras.layers.BatchNormalization()(x)
        
        # Segunda capa convolucional
        x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        
        # Tercera capa convolucional
        x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        
        # Flatten y capas densas
        x = tf.keras.layers.Flatten()(x)
        x = tf.keras.layers.Dense(256, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        
        # Outputs
        left_click = tf.keras.layers.Dense(ROWS * COLS, activation='sigmoid', name='left')(x)
        right_click = tf.keras.layers.Dense(ROWS * COLS, activation='sigmoid', name='right')(x)
        
        # Crear modelo
        self.model = tf.keras.models.Model(inputs=input_layer, outputs=[left_click, right_click])
        
        # Compilar
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss={'left': 'binary_crossentropy', 'right': 'binary_crossentropy'},
            metrics={'left': 'accuracy', 'right': 'accuracy'}
        )
        
        return self.model
    
    def load_model(self, path):
        """Carga un modelo guardado"""
        try:
            self.model = tf.keras.models.load_model(path)
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                loss={'left': 'binary_crossentropy', 'right': 'binary_crossentropy'},
                metrics={'left': 'accuracy', 'right': 'accuracy'}
            )
            print(f"✅ Modelo cargado desde {path}")
            return True
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return False
    
    def save_model(self, path):
        """Guarda el modelo"""
        if self.model:
            self.model.save(path)
            print(f"✅ Modelo guardado en {path}")
    
    def predict(self, state):
        """Hace predicción"""
        if self.model is None:
            return None, None
            
        try:
            # Añadir dimensión de batch si es necesario
            if len(state.shape) == 3:
                state = np.expand_dims(state, axis=0)
            
            left_probs, right_probs = self.model.predict(state, verbose=0)
            
            # Reshape a formato de tablero
            left_probs = left_probs[0].reshape(ROWS, COLS)
            right_probs = right_probs[0].reshape(ROWS, COLS)
            
            return left_probs, right_probs
        except Exception as e:
            print(f"❌ Error en predicción: {e}")
            return None, None
    
    def train(self, X, y, epochs=5000, batch_size=64, validation_split=0.2):
        """Entrena el modelo"""
        if self.model is None:
            self.create_model()
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss', 
                patience=20, 
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss', 
                factor=0.5, 
                patience=5,
                min_lr=1e-7
            )
        ]
        
        # Entrenar
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        
        return history

def board_to_state(screen, analyzer):
    """Convierte el estado del tablero a array numpy para la IA"""
    state = np.zeros((ROWS, COLS, 6), dtype=np.float32)
    
    # Analizar estado de la carita (juego activo/inactivo)
    face_state, _, _ = analyzer.analyze_face_state(screen)
    game_active = 1.0 if "Sonriendo" in face_state else 0.0
    
    for row in range(ROWS):  # filas (y)
        for col in range(COLS):  # columnas (x)
            tile_type, _, _ = analyzer.analyze_tile(screen, col, row)
            
            # Features por casilla:
            # 0: Sin revelar (1.0) o revelada (0.0)
            # 1: Tiene bandera (1.0) o no (0.0)
            # 2: Es número (1.0) o no (0.0)
            # 3: Es espacio vacío (1.0) o no (0.0)
            # 4: Valor del número (0.0-1.0, normalizado)
            # 5: Estado del juego (1.0 activo, 0.0 inactivo)
            
            features = np.zeros(6, dtype=np.float32)
            
            if tile_type == "Sin revelar":
                features[0] = 1.0
            elif tile_type == "Bandera":
                features[1] = 1.0
            elif "Número" in tile_type:
                features[2] = 1.0
                try:
                    number = int(tile_type.split()[-1])
                    features[4] = float(number) / 8.0  # Normalizar 1-8 -> 0.125-1.0
                except:
                    features[4] = 0.0
            elif tile_type == "Espacio vacío":
                features[3] = 1.0
            
            features[5] = game_active
            state[row, col] = features
    
    return state