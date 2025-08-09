import numpy as np
from collections import deque
from settings import ROWS, COLS
from agents.hybrid_agent import HybridAgent
from training.train import create_model
from training.data_generator import TrainingGame

class DataCollector:
    def __init__(self, max_samples=10000):
        self.states = deque(maxlen=max_samples)
        self.left_targets = deque(maxlen=max_samples)
        self.right_targets = deque(maxlen=max_samples)
    
    def add_sample(self, state, left_target, right_target):
        self.states.append(state)
        self.left_targets.append(left_target)
        self.right_targets.append(right_target)
    
    def get_dataset(self):
        return (
            np.array(self.states),
            [np.array(self.left_targets), np.array(self.right_targets)]
        )

# Configuración de entrenamiento
model = create_model(ROWS, COLS)
collector = DataCollector()
agent = HybridAgent(model)

# Jugar 100 partidas para recopilar datos
for _ in range(100):
    game = TrainingGame(collector)
    game.run()

# Entrenar el modelo
X, y = collector.get_dataset()
model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2)

# Guardar modelo entrenado
# model.save('minesweeper_model.h5')
model.save('../models/minesweeper_model.h5')