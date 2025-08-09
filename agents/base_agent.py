import numpy as np

class BaseAgent:
    def predict_action(self, state):
        raise NotImplementedError