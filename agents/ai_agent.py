import numpy as np
from agents.base_agent import BaseAgent
from agents.rules_agent import RulesAgent
from settings import ROWS, COLS

class AIAgent(BaseAgent):
    def __init__(self, model=None):
        super().__init__()
        self.model = model
        self.rules_agent = RulesAgent()
        
    def predict_action(self, state, flags_remaining=None):
        # Primero intentar con reglas lógicas (más confiables)
        rule_action = self.rules_agent.predict_action(state, flags_remaining)
        if rule_action:
            print(f"🔧 Regla sugiere: {rule_action}")
            return rule_action
        
        # Si las reglas no encuentran nada, usar la red neuronal
        if self.model and self.model.model:
            return self._neural_prediction(state, flags_remaining)
        
        print("❓ No hay acción disponible")
        return None
    
    def _neural_prediction(self, state, flags_remaining):
        """Predicción usando la red neuronal"""
        try:
            left_probs, right_probs = self.model.predict(state)
            
            if left_probs is None or right_probs is None:
                return None
            
            # Filtrar acciones inválidas
            left_probs = self._filter_invalid_actions(left_probs, state)
            right_probs = self._filter_invalid_actions(right_probs, state)
            
            # Aplicar restricción de banderas
            if flags_remaining is not None and flags_remaining <= 0:
                right_probs = np.zeros_like(right_probs)
            
            # Encontrar la mejor acción
            max_left = np.max(left_probs)
            max_right = np.max(right_probs)
            
            # Umbral mínimo de confianza
            threshold = 0.3
            
            if max_left > max_right and max_left > threshold:
                row, col = np.unravel_index(np.argmax(left_probs), left_probs.shape)
                print(f"🧠 IA sugiere LEFT en ({row},{col}) prob:{max_left:.3f}")
                return ('left', row, col)
            elif max_right > threshold:
                row, col = np.unravel_index(np.argmax(right_probs), right_probs.shape)
                print(f"🧠 IA sugiere RIGHT en ({row},{col}) prob:{max_right:.3f}")
                return ('right', row, col)
            
        except Exception as e:
            print(f"❌ Error en predicción neuronal: {e}")
        
        return None
    
    def _filter_invalid_actions(self, probs, state):
        filtered_probs = np.copy(probs)
        
        for row in range(ROWS):
            for col in range(COLS):
                # Verificar si la casilla está disponible para acciones
                is_hidden = state[row, col, 0] > 0.5      # Sin revelar
                has_flag = state[row, col, 1] > 0.5       # Con bandera
                is_revealed = (not is_hidden) and (not has_flag)  # Revelada
                
                # Solo permitir acciones en casillas sin revelar y sin bandera
                if is_revealed or has_flag:
                    filtered_probs[row, col] = 0.0
        
        return filtered_probs
    
    def set_model(self, model):
        """Asigna un modelo al agente"""
        self.model = model
        print("✅ Modelo asignado al agente")
        
    def get_action_probabilities(self, state):
        """Devuelve las probabilidades de acción sin filtrar (para análisis)"""
        if self.model and self.model.model:
            return self.model.predict(state)
        return None, None