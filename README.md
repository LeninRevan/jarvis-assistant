# 🤖 J.A.R.V.I.S. Assistant

> *"Tecnología creada para asistir, colaborar y mejorar la calidad de vida de las personas."*

JARVIS es un asistente de inteligencia artificial autónomo, multimodal y extensible, diseñado para interactuar mediante **visión en tiempo real**, **voz continua bidireccional** y **ejecución de acciones mediante Tool Calling (Function Calling)**.

Funciona tanto de forma **100% local y privada** (usando Ollama o LM Studio) como conectado a APIs de vanguardia (Google Gemini, OpenAI).

---

## 🚀 Características Principales

- 🎙 **Entrada por Voz Local (STT):** Integración con `faster-whisper` y detección de actividad por voz (VAD). Escucha, detecta cuando terminas de hablar y transcribe al instante sin enviar tu audio a la nube.
- 🔊 **Voz Neuronal Natural (TTS):** Voces en español hiperrealistas mediante `edge-tts` (ej. `es-MX-DaliaNeural` o `es-MX-JorgeNeural`), sin costo de API ni retardos mecánicos.
- 📸 **Percepción Visual 1080p:** Captura de fotogramas nítidos desde tu cámara web o capturas de tu pantalla actual (desktop vision) para analizar circuitos, cables, documentos o interfaces.
- ⚙ **Sistema Extensible de Tool Calling:** El modelo puede invocar comandos de shell, leer archivos del sistema, revisar el estado del hardware y disparar scripts en tu máquina de manera autónoma.
- 🔄 **Compatibilidad Multi-Backend:**
  - **Local:** Ollama (`llama3.2-vision`, `llava`, `qwen2.5-coder`), LM Studio, vLLM.
  - **Cloud:** Google Gemini (`gemini-2.5-flash`), OpenAI (`gpt-4o-mini`, `gpt-4o`).

---

## 📁 Arquitectura del Proyecto

```text
jarvis-assistant/
├── config.py                 # Configuración tipada y carga de variables de entorno
├── .env.example              # Plantilla para configurar proveedores y dispositivos
├── run.sh                    # Lanzador inteligente (gestiona venv y dependencias)
├── requirements.txt          # Dependencias de Python verificadas
├── main.py                   # CLI principal con soporte de modos interactivos
└── jarvis/
    ├── agent.py              # Bucle de percepción, razonamiento, herramientas y habla
    ├── backends/             # Conectores intercambiables (OpenAI/Ollama, Gemini)
    │   ├── base.py           # Interfaz abstracta del LLM
    │   ├── openai_client.py  # Compatible con Ollama, LM Studio y OpenAI
    │   └── gemini_client.py  # Conector nativo de Google Gemini
    ├── vision/               # Captura de cámara y pantalla con ffmpeg
    │   └── capture.py
    ├── audio/                # Motores de reconocimiento (STT) y síntesis (TTS)
    │   ├── stt.py            # Faster-Whisper con detección de silencios
    │   └── tts.py            # Edge-TTS en español neutro / mexicano
    └── tools/                # Registro dinámico de herramientas (@tool)
        ├── registry.py       # Conversor automático de funciones Python a JSON Schema
        ├── system_tools.py   # Shell, CPU, RAM, hora actual
        └── files_tools.py    # Lectura y listado seguro de archivos
```

---

## 🛠 Requisitos del Sistema

1. **Linux / macOS / Windows (WSL2)**
2. **Python 3.10+**
3. Herramientas del sistema recomendadas:
   ```bash
   sudo apt install ffmpeg libasound2-dev libportaudio2 pulseaudio-utils
   ```

---

## ⚡ Instalación Rápida

1. **Clonar o acceder a la carpeta del proyecto:**
   ```bash
   cd ~/Documentos/jarvis-assistant
   ```

2. **Configurar tu backend:**
   Copia `.env.example` a `.env` y define tu modelo preferido:
   ```bash
   cp .env.example .env
   nano .env
   ```

   - **Si usas Ollama Local:**
     ```env
     LLM_PROVIDER=ollama
     LLM_BASE_URL=http://localhost:11434/v1
     LLM_MODEL=llama3.2-vision
     ```

   - **Si usas Google Gemini:**
     ```env
     LLM_PROVIDER=gemini
     GEMINI_API_KEY=tu_clave_aqui
     LLM_MODEL=gemini-2.5-flash
     ```

3. **Iniciar el asistente:**
   ```bash
   ./run.sh
   ```
   *(El script configurará automáticamente el entorno virtual en el primer arranque).*

---

## 🎮 Modos de Uso

### 1. Modo Voz Continua (Manos Libres)
JARVIS escuchará a través de tu micrófono, responderá con su voz y analizará la cámara automáticamente si tu pregunta lo amerita:
```bash
./run.sh --voice
```

### 2. Modo Consola Interactiva
Permite chatear por texto, invocar herramientas y adjuntar imágenes manualmente con comandos:
```bash
./run.sh
```
- Escribe `/cam [tu pregunta]` para adjuntar una foto de tu webcam.
- Escribe `/screen [tu pregunta]` para que analice lo que tienes abierto en tu monitor.

### 3. Consulta Rápida (One-Shot)
```bash
./run.sh --once "Revisa los archivos en mi carpeta actual"
./run.sh --once "¿Qué objeto tengo en mi mano?" --cam
```

---

## 🧩 Cómo Agregar Nuevas Herramientas (Tool Calling)

Cualquier persona puede agregar nuevas funciones a JARVIS simplemente decorando una función de Python con `@tool`. JARVIS inspeccionará los tipos y los docstrings para aprender a usarla:

```python
# En jarvis/tools/mi_herramienta.py
from .registry import tool

@tool
def encender_luz_escritorio(brillo: int = 100) -> str:
    \"\"\"Enciende la luz inteligente del escritorio ajustando el brillo de 0 a 100.\"\"\"
    # Aquí puedes llamar a Home Assistant, MQTT, o una petición HTTP
    return f"Luz de escritorio encendida al {brillo}% de potencia."
```

¡Y listo! Al reiniciar JARVIS, la herramienta estará disponible para el modelo automáticamente.
