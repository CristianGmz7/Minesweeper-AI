import tensorflow as tf
import numpy as np
from settings import ROWS, COLS
from agents.base_agent import BaseAgent
from agents.rules_agent import RulesAgent

class HybridAgent(BaseAgent):
    def __init__(self, model=None, model_path=None):
        """
        Inicializa el agente híbrido.
        
        Args:
            model: Modelo pre-cargado de Keras (opcional)
            model_path: Ruta al modelo guardado (opcional)
        """
        super().__init__()
        self.rules_agent = RulesAgent()
        
        # Cargar modelo según los parámetros recibidos
        if model_path:
            try:
                self.model = tf.keras.models.load_model(model_path)
                print(f"✅ Modelo cargado desde {model_path}")
            except Exception as e:
                print(f"⚠️ Error cargando modelo: {e}")
                self.model = None
        elif model:
            self.model = model
            print("✅ Modelo recibido directamente")
        else:
            self.model = None
            print("⚠️ No se proporcionó modelo, usando solo reglas")
        
        # Verificar que el modelo esté compilado
        if self.model:
            try:
                if not hasattr(self.model, 'optimizer'):
                    print("🔷 Compilando modelo con configuración por defecto")
                    self.model.compile(optimizer='adam',
                                    loss={'left': 'binary_crossentropy', 
                                          'right': 'binary_crossentropy'})
            except Exception as e:
                print(f"⚠️ Error verificando modelo: {e}")

    def predict_action(self, state):
        """
        Predice una acción usando primero reglas y luego el modelo neuronal.
        
        Args:
            state: Estado actual del tablero
            
        Returns:
            Tupla (tipo_accion, x, y) o None si no hay acción clara
        """
        # Primero probar con reglas
        rule_action = self.rules_agent.predict_action(state)
        if rule_action:
            return rule_action
        
        # Si no hay regla aplicable y tenemos modelo, usarlo
        if self.model:
            try:
                # Preprocesamiento adicional si es necesario
                processed_state = self._preprocess_state(state)
                
                # Predicción
                left_probs, right_probs = self.model.predict(processed_state[np.newaxis, ...], verbose=0)
                left_probs = left_probs[0].reshape(ROWS, COLS)
                right_probs = right_probs[0].reshape(ROWS, COLS)
                
                # Filtrar casillas ya reveladas o marcadas
                left_probs = self._filter_invalid_actions(left_probs, state)
                right_probs = self._filter_invalid_actions(right_probs, state)
                
                # Selección de acción
                max_left = np.unravel_index(np.argmax(left_probs), left_probs.shape)
                max_right = np.unravel_index(np.argmax(right_probs), right_probs.shape)
                
                if left_probs[max_left] > right_probs[max_right] and left_probs[max_left] > 0.5:
                    return ('left', max_left[0], max_left[1])
                elif right_probs[max_right] > 0.5:
                    return ('right', max_right[0], max_right[1])
                
            except Exception as e:
                print(f"⚠️ Error en predicción del modelo: {e}")
        
        return None

    def _preprocess_state(self, state):
        """Preprocesa el estado para el modelo"""
        # Puedes añadir transformaciones aquí si es necesario
        return state

    def _filter_invalid_actions(self, probs, state):
        """
        Filtra casillas ya reveladas o marcadas.
        
        Args:
            probs: Matriz de probabilidades
            state: Estado del tablero
            
        Returns:
            Matriz de probabilidades con acciones inválidas anuladas
        """
        # Crear máscara de casillas inválidas (ya reveladas o con bandera)
        invalid_mask = (state[..., 0] < 0.5) | (state[..., 1] > 0.5)  # No reveladas o con bandera
        
        # Aplicar máscara
        filtered_probs = np.copy(probs)
        filtered_probs[invalid_mask] = 0
        
        return filtered_probs