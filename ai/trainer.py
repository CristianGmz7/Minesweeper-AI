import os
import numpy as np
from ai.model import MinesweeperModel
from ai.data_collector import DataCollector

class MinesweeperTrainer:
    def __init__(self, model_path="models/minesweeper_model.h5"):
        self.model_path = model_path
        self.model = MinesweeperModel()
        self.data_collector = DataCollector()
        
        # Crear directorio de modelos
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    def train_from_rules(self, num_samples=5000, epochs=30):
        """
        Entrenamiento automático usando solo reglas lógicas
        """
        print("🤖 Entrenamiento automático con reglas")
        print("=" * 50)
        
        # Generar datos con reglas
        print("1️⃣ Generando datos de entrenamiento...")
        samples = self.data_collector.generate_rule_based_data(num_samples)
        
        if samples < 100:
            print("❌ No se generaron suficientes datos")
            return None
        
        # Entrenar modelo
        print("2️⃣ Entrenando modelo...")
        return self._train_model(epochs=epochs)
    
    def train_from_saved_data(self, data_path="data/training_data.pkl", epochs=50):
        """
        Entrenamiento usando datos guardados previamente
        """
        print("📂 Entrenamiento con datos guardados")
        print("=" * 50)
        
        # Cargar datos
        self.data_collector.load_data(data_path)
        
        if self.data_collector.sample_count < 100:
            print("❌ Datos insuficientes. Necesitas al menos 100 muestras.")
            return None
        
        # Entrenar
        return self._train_model(epochs=epochs)
    
    def train_mixed(self, rule_samples=3000, manual_data_path="data/training_data.pkl", epochs=50):
        """
        Entrenamiento mixto: reglas + datos manuales
        """
        print("🔄 Entrenamiento mixto")
        print("=" * 50)
        
        # Limpiar datos previos
        self.data_collector.clear_data()
        
        # 1. Generar datos con reglas
        print("1️⃣ Generando datos base con reglas...")
        rule_samples_generated = self.data_collector.generate_rule_based_data(rule_samples)
        
        # 2. Cargar datos manuales si existen
        print("2️⃣ Cargando datos manuales...")
        if os.path.exists(manual_data_path):
            manual_collector = DataCollector()
            manual_collector.load_data(manual_data_path)
            
            # Combinar datos
            self.data_collector.states.extend(manual_collector.states)
            self.data_collector.left_targets.extend(manual_collector.left_targets)
            self.data_collector.right_targets.extend(manual_collector.right_targets)
            self.data_collector.sample_count = len(self.data_collector.states)
            
            print(f"📊 Datos combinados: {self.data_collector.sample_count} muestras")
        
        # 3. Entrenar
        print("3️⃣ Entrenando modelo final...")
        return self._train_model(epochs=epochs)
    
    def _train_model(self, epochs=30, learning_rate=0.001):
        """Entrena el modelo con los datos actuales"""
        # Obtener dataset
        X, y = self.data_collector.get_dataset()
        
        if X is None:
            return None
        
        print(f"📊 Entrenando con {len(X)} muestras por {epochs} épocas")
        
        # Crear o cargar modelo
        if os.path.exists(self.model_path):
            print("📂 Cargando modelo existente...")
            if not self.model.load_model(self.model_path):
                print("🔷 Creando nuevo modelo...")
                self.model.create_model()
        else:
            print("🔷 Creando nuevo modelo...")
            self.model.create_model()
        
        # Entrenar
        try:
            history = self.model.train(
                X, y,
                epochs=epochs,
                batch_size=16,  # Batch pequeño para mejor convergencia
                validation_split=0.15
            )
            
            # Guardar modelo
            self.model.save_model(self.model_path)
            
            # Mostrar resultados
            final_loss = history.history['val_loss'][-1] if 'val_loss' in history.history else 'N/A'
            print(f"✅ Entrenamiento completado. Loss final: {final_loss}")
            
            return self.model
            
        except Exception as e:
            print(f"❌ Error durante entrenamiento: {e}")
            return None
    
    def evaluate_model(self, test_games=10):
        """Evalúa el rendimiento del modelo"""
        if not os.path.exists(self.model_path):
            print("❌ No hay modelo para evaluar")
            return
        
        print("📊 Evaluando modelo...")
        
        # Cargar modelo
        model = MinesweeperModel()
        if not model.load_model(self.model_path):
            return
        
        from agents.ai_agent import AIAgent
        from game.game import Game
        from ai.model import board_to_state
        import pygame
        
        # Inicializar pygame
        if not pygame.get_init():
            pygame.init()
            pygame.display.set_mode((400, 400))
        
        agent = AIAgent(model)
        wins = 0
        total_moves = 0
        
        for game_num in range(test_games):
            game = Game()
            moves_in_game = 0
            
            while game.game_active and moves_in_game < 200:
                state = board_to_state(game.screen, game.tile_analyzer)
                action = agent.predict_action(state, game.flags_remaining)
                
                if not action:
                    break
                
                action_type, row, col = action
                
                try:
                    if action_type == 'left':
                        if not game.board.dig(col, row):
                            break  # Game over
                    elif action_type == 'right':
                        tile = game.board.board_list[col][row]
                        if not tile.revealed and not tile.flagged and game.flags_remaining > 0:
                            tile.flagged = True
                            game.flags_remaining -= 1
                except:
                    break
                
                moves_in_game += 1
                game.draw()
                pygame.display.flip()
            
            if game.check_win():
                wins += 1
            
            total_moves += moves_in_game
            print(f"Juego {game_num + 1}: {'Ganado' if game.check_win() else 'Perdido'} ({moves_in_game} movimientos)")
        
        win_rate = (wins / test_games) * 100
        avg_moves = total_moves / test_games
        
        print(f"\n📈 Resultados de evaluación:")
        print(f"   Tasa de victoria: {win_rate:.1f}% ({wins}/{test_games})")
        print(f"   Movimientos promedio: {avg_moves:.1f}")
        
        return win_rate, avg_moves

# Función de utilidad para entrenamiento rápido
def quick_train(method='mixed'):
    """
    Función de entrenamiento rápido
    
    Args:
        method: 'rules' (solo reglas), 'mixed' (mixto), 'manual' (solo datos manuales)
    """
    trainer = MinesweeperTrainer()
    
    if method == 'rules':
        model = trainer.train_from_rules(num_samples=3000, epochs=25)
    elif method == 'mixed':
        model = trainer.train_mixed(rule_samples=2000, epochs=40)
    elif method == 'manual':
        model = trainer.train_from_saved_data(epochs=50)
    else:
        print(f"❌ Método inválido: {method}")
        return None
    
    if model:
        print("\n🎯 ¿Quieres evaluar el modelo entrenado? (y/n)")
        if input().lower() == 'y':
            trainer.evaluate_model(test_games=5)
    
    return model