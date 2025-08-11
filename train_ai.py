#!/usr/bin/env python3
"""
Script simple para entrenar la IA de Minesweeper
"""

import os
import sys

def main():
    print("🎯 Entrenador de IA para Minesweeper")
    print("=" * 50)
    
    # Crear directorios necesarios
    os.makedirs("models", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    print("\nOpciones de entrenamiento:")
    print("1. 🤖 Automático (solo reglas lógicas) - Rápido")
    print("2. 🎮 Manual (juegas tú) - Mejor calidad")
    print("3. 🔄 Mixto (reglas + manual) - Recomendado")
    print("4. 📊 Evaluar modelo existente")
    print("5. 🧹 Limpiar datos y empezar de cero")
    
    while True:
        choice = input("\nSelecciona opción (1-5): ").strip()
        
        if choice == '1':
            train_automatic()
            break
        elif choice == '2':
            train_manual()
            break
        elif choice == '3':
            train_mixed()
            break
        elif choice == '4':
            evaluate_model()
            break
        elif choice == '5':
            clean_data()
            continue
        else:
            print("❌ Opción inválida. Usa números del 1 al 5.")

def train_automatic():
    """Entrenamiento completamente automático"""
    print("\n🤖 Entrenamiento automático iniciado")
    print("-" * 30)
    
    from ai.trainer import MinesweeperTrainer
    
    trainer = MinesweeperTrainer()
    
    # Configurar parámetros
    samples = int(input("¿Cuántas muestras generar? (recomendado 3000-5000): ") or "3000")
    epochs = int(input("¿Cuántas épocas de entrenamiento? (recomendado 25-40): ") or "30")
    
    print(f"\n🔄 Generando {samples} muestras y entrenando por {epochs} épocas...")
    
    model = trainer.train_from_rules(num_samples=samples, epochs=epochs)
    
    if model:
        print("✅ Entrenamiento completado!")
        
        # Preguntar si quiere evaluar
        if input("¿Evaluar el modelo? (y/n): ").lower() == 'y':
            trainer.evaluate_model(test_games=10)
    else:
        print("❌ Error durante el entrenamiento")

def train_manual():
    """Entrenamiento con datos manuales"""
    print("\n🎮 Entrenamiento manual")
    print("-" * 30)
    print("Vas a jugar Minesweeper para generar datos de entrenamiento.")
    print("¡La calidad de la IA dependerá de qué tan bien juegues!")
    
    from ai.training_game import manual_data_collection
    from ai.trainer import MinesweeperTrainer
    
    # Recolectar datos jugando
    collector = manual_data_collection()
    
    if collector.sample_count > 50:
        print(f"\n🧠 Entrenando con {collector.sample_count} muestras...")
        
        trainer = MinesweeperTrainer()
        epochs = int(input("¿Cuántas épocas? (recomendado 40-60): ") or "50")
        
        # Cargar datos en el entrenador
        trainer.data_collector = collector
        
        model = trainer._train_model(epochs=epochs)
        
        if model:
            print("✅ Modelo entrenado con tus datos!")
            if input("¿Evaluar el modelo? (y/n): ").lower() == 'y':
                trainer.evaluate_model(test_games=5)
        else:
            print("❌ Error durante el entrenamiento")
    else:
        print("❌ No se recolectaron suficientes datos para entrenar")

def train_mixed():
    """Entrenamiento mixto (recomendado)"""
    print("\n🔄 Entrenamiento mixto")
    print("-" * 30)
    print("Este método combina datos automáticos (reglas) con datos manuales")
    print("para obtener el mejor resultado.")
    
    from ai.trainer import MinesweeperTrainer
    
    trainer = MinesweeperTrainer()
    
    # Paso 1: Datos automáticos
    print("\n1️⃣ Generando datos base con reglas...")
    rule_samples = int(input("¿Cuántas muestras automáticas? (recomendado 2000): ") or "2000")
    
    # Paso 2: Datos manuales (opcional)
    manual_data = input("¿Quieres añadir datos manuales jugando? (y/n): ").lower() == 'y'
    
    if manual_data:
        print("\n2️⃣ Ahora juega algunas partidas para mejorar la IA:")
        from ai.training_game import manual_data_collection
        manual_data_collection()
    
    # Paso 3: Entrenamiento
    print("\n3️⃣ Entrenando modelo final...")
    epochs = int(input("¿Cuántas épocas? (recomendado 40): ") or "40")
    
    model = trainer.train_mixed(
        rule_samples=rule_samples,
        epochs=epochs
    )
    
    if model:
        print("✅ Entrenamiento mixto completado!")
        if input("¿Evaluar el modelo? (y/n): ").lower() == 'y':
            trainer.evaluate_model(test_games=10)
    else:
        print("❌ Error durante el entrenamiento")

def evaluate_model():
    """Evalúa un modelo existente"""
    model_path = "models/minesweeper_model.h5"
    
    if not os.path.exists(model_path):
        print("❌ No se encontró modelo para evaluar")
        print(f"Busca el archivo: {model_path}")
        return
    
    print("\n📊 Evaluando modelo existente...")
    
    from ai.trainer import MinesweeperTrainer
    
    trainer = MinesweeperTrainer(model_path)
    
    games = int(input("¿Cuántos juegos de prueba? (recomendado 10): ") or "10")
    
    win_rate, avg_moves = trainer.evaluate_model(test_games=games)
    
    print(f"\n📈 Resultados:")
    print(f"Tasa de victoria: {win_rate:.1f}%")
    print(f"Movimientos promedio: {avg_moves:.1f}")
    
    if win_rate > 30:
        print("🎉 ¡Modelo funciona bien!")
    elif win_rate > 10:
        print("👍 Modelo decente, pero se puede mejorar")
    else:
        print("😅 Modelo necesita más entrenamiento")

def clean_data():
    """Limpia datos de entrenamiento"""
    print("\n🧹 Limpiando datos...")
    
    data_files = [
        "data/training_data.pkl",
        "models/minesweeper_model.h5"
    ]
    
    removed = 0
    for file_path in data_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Eliminado: {file_path}")
            removed += 1
    
    if removed == 0:
        print("✅ No había datos que limpiar")
    else:
        print(f"✅ {removed} archivos eliminados")

def quick_start():
    """Inicio rápido para usuarios impacientes"""
    print("\n⚡ Inicio rápido")
    print("Generando modelo básico en 2 minutos...")
    
    from ai.trainer import quick_train
    
    model = quick_train('rules')  # Solo reglas, rápido
    
    if model:
        print("✅ ¡Listo! Prueba la IA con: python ai_main.py")
    else:
        print("❌ Error en inicio rápido")

def show_instructions():
    """Muestra instrucciones detalladas"""
    print("\n" + "="*60)
    print("📖 INSTRUCCIONES DETALLADAS")
    print("="*60)
    print()
    print("🎯 TIPOS DE ENTRENAMIENTO:")
    print()
    print("1. AUTOMÁTICO:")
    print("   • Usa solo reglas lógicas del Minesweeper")
    print("   • Muy rápido (2-5 minutos)")
    print("   • Bueno para empezar")
    print("   • Limitado a situaciones obvias")
    print()
    print("2. MANUAL:")
    print("   • Tú juegas y la IA aprende de tus movimientos")
    print("   • Más lento (depende de cuánto juegues)")
    print("   • Mejor calidad si juegas bien")
    print("   • Requiere paciencia")
    print()
    print("3. MIXTO (RECOMENDADO):")
    print("   • Combina ambos métodos")
    print("   • Balance entre velocidad y calidad")
    print("   • Mejor opción para la mayoría")
    print()
    print("🎮 CÓMO JUGAR PARA ENTRENAR:")
    print("   • Haz movimientos lógicos y seguros")
    print("   • Evita clicks aleatorios")
    print("   • Usa las reglas básicas del Minesweeper")
    print("   • Entre más juegues mejor, pero 20-30 partidas están bien")
    print()
    print("📊 EVALUACIÓN:")
    print("   • Tasa de victoria > 30% = Excelente")
    print("   • Tasa de victoria > 15% = Bueno")
    print("   • Tasa de victoria < 10% = Necesita más entrenamiento")
    print()
    print("="*60)

if __name__ == "__main__":
    # Verificar si quiere instrucciones detalladas
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_instructions()
    elif len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_start()
    else:
        main()