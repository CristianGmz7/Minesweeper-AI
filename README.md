# 🎯 Minesweeper IA

Una implementación de Minesweeper con inteligencia artificial que combina reglas lógicas con redes neuronales.

## Antes de iniciar:
Descargar la carpeta assets del siguiente enlace
https://drive.google.com/file/d/1qNDsIoYWTcJMupDhne5Oqp-aNvGwD7VD/view?usp=sharing

Descomprimir el archivo .rar y colocarlo en la raiz del proyecto clonado, al mismo nivel de las carpetas agents, ai, data, game, models, utils y de los archivos ai_main.py, main.py, settings.py, train_ai.py 

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
pip install tensorflow numpy pygame
```

### 2. Entrenar la IA (escoge una opción):

**Opción A - Automático (2-3 minutos):**
```bash
python train_ai.py
# Selecciona opción 1
```

**Opción B - Súper rápido:**
```bash
python train_ai.py --quick
```

### 3. Jugar con IA
```bash
python ai_main.py
```

## 📁 Estructura del Proyecto

```
minesweeper-ai/
├── 🎮 game/              # Motor del juego
│   ├── game.py           # Juego principal
│   ├── board.py          # Lógica del tablero
│   └── sprites.py        # Sprites y elementos visuales
├── 🤖 ai/                # Sistema de IA
│   ├── model.py          # Red neuronal
│   ├── trainer.py        # Sistema de entrenamiento
│   ├── data_collector.py # Recolección de datos
│   └── training_game.py  # Juego para entrenar
├── 🧠 agents/            # Agentes de IA
│   ├── base_agent.py     # Clase base
│   ├── rules_agent.py    # Agente con reglas lógicas
│   └── ai_agent.py       # Agente híbrido (reglas + IA)
├── 🛠️ utils/             # Utilidades
│   └── tile_analyzer.py  # Análisis visual del tablero
├── 📊 models/            # Modelos entrenados
├── 📁 data/              # Datos de entrenamiento
├── 🎨 assets/            # Sprites del juego
├── train_ai.py           # Script principal de entrenamiento
├── ai_main.py            # Juego con IA
├── main.py               # Juego normal (sin IA)
└── settings.py           # Configuración
```

## 🎯 Tipos de Entrenamiento

### 🤖 Automático
- **Tiempo**: 2-5 minutos
- **Calidad**: Buena para situaciones básicas
- **Ventaja**: No requiere intervención humana
- **Desventaja**: Limitado a reglas obvias

```bash
python train_ai.py  # Opción 1
```

### 🎮 Manual
- **Tiempo**: Depende de ti (20-30 partidas recomendadas)
- **Calidad**: Excelente si juegas bien
- **Ventaja**: La IA aprende estrategias complejas
- **Desventaja**: Requiere tiempo y habilidad

```bash
python train_ai.py  # Opción 2
```

### 🔄 Mixto (Recomendado)
- **Tiempo**: 5-10 minutos + tu tiempo jugando
- **Calidad**: Excelente balance
- **Ventaja**: Mejor de ambos mundos
- **Desventaja**: Un poco más complejo

```bash
python train_ai.py  # Opción 3
```

## 🎮 Controles del Juego

### Juego Normal
- **Clic izquierdo**: Revelar casilla
- **Clic derecho**: Colocar/quitar bandera
- **R**: Reiniciar juego

### Juego con IA
- **ESPACIO**: Activar/desactivar IA
- **H**: Mostrar ayuda
- **R**: Reiniciar juego
- **ESC**: Salir

## 📊 Evaluación del Modelo

### Métricas de Rendimiento
- **> 30% victoria**: 🎉 Excelente
- **> 15% victoria**: 👍 Bueno  
- **< 10% victoria**: 😅 Necesita más entrenamiento

### Evaluar modelo existente
```bash
python train_ai.py  # Opción 4
```

## 🔧 Archivos Importantes

### Eliminar estos archivos del proyecto original:
- `training/data_collector.py` (duplicado)
- `training/data_generator.py` (problemático)  
- `training/collector.py` (obsoleto)
- `training/train.py` (confuso)
- `main_training.py` (innecesario)
- `quick_start.py` (redundante)
- `test_coordinates.py` (temporal)

### Mantener estos archivos:
- `settings.py` ✅
- `main.py` ✅
- `game/` (toda la carpeta) ✅
- `utils/tile_analyzer.py` ✅
- `assets/` (toda la carpeta) ✅

## 🎯 Consejos para Mejor Rendimiento

### Para Entrenamiento Manual:
1. **Juega lógicamente**: Usa las reglas básicas del Minesweeper
2. **Evita clicks aleatorios**: La IA aprenderá malos hábitos
3. **Sé consistente**: Usa las mismas estrategias
4. **Juega 20-30 partidas**: Más datos = mejor IA

### Para Mejorar la IA:
1. **Combina métodos**: Usa entrenamiento mixto
2. **Más épocas**: Si tienes tiempo, usa 50-80 épocas
3. **Evalúa regularmente**: Prueba la IA después de entrenar
4. **Reentrenar**: Si no funciona bien, añade más datos

## 📈 Arquitectura de la IA

### Sistema Híbrido:
1. **Reglas Lógicas** (Prioridad alta)
   - Casillas seguras por números satisfechos
   - Minas obvias por conteo
   
2. **Red Neuronal** (Cuando las reglas fallan)
   - CNN con 3 capas convolucionales
   - 2 salidas: clic izquierdo y derecho
   - Entrenada con datos de reglas + jugadas humanas

### Características del Estado:
- Sin revelar (0/1)
- Con bandera (0/1)  
- Es número (0/1)
- Es espacio vacío (0/1)
- Valor numérico (0.0-1.0)
- Estado del juego (0/1)

## 📝 Notas Técnicas

- **Pygame**: Para interfaz gráfica y captura de pantalla
- **TensorFlow**: Para la red neuronal
- **NumPy**: Para manejo de arrays
- **Sin mouse**: La IA lee directamente la pantalla (píxeles)
- **Coordenadas**: Sistema (fila, columna) consistente

---

¡Diviértete jugando y entrenando tu IA de Minesweeper! 🎮🤖
