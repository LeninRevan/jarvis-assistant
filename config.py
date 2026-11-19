"""
JARVIS Assistant - Módulo de Configuración Unificado
Soporta proveedores locales (Ollama, LM Studio) y en la nube (Gemini, OpenAI, Anthropic).
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_SYSTEM_PROMPT = """Eres JARVIS, un asistente de inteligencia artificial avanzado, autónomo y altamente competente.
Tu misión es asistir al usuario en tiempo real con razonamiento profundo, claridad técnica y tono profesional pero cercano y colaborativo.
Tienes capacidades visuales (puedes ver lo que tu usuario te muestra a través de su cámara o capturas) y herramientas del sistema (tool calling).
Respuestas concisas, precisas y accionables por defecto, a menos que el usuario te pida explicaciones a fondo."""

@dataclass
class JarvisConfig:
    # LLM Settings
    provider: str = os.getenv("LLM_PROVIDER", "gemini").lower()  # gemini, ollama, lmstudio, openai
    api_key: str = os.getenv("LLM_API_KEY", os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", "")))
    base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    model: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    system_prompt: str = os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)
    temperature: float = float(os.getenv("TEMPERATURE", "0.4"))

    # Audio Settings
    stt_enabled: bool = os.getenv("STT_ENABLED", "true").lower() in ("true", "1", "yes")
    stt_model_size: str = os.getenv("STT_MODEL_SIZE", "base")  # tiny, base, small
    stt_language: str = os.getenv("STT_LANGUAGE", "es")
    
    tts_enabled: bool = os.getenv("TTS_ENABLED", "true").lower() in ("true", "1", "yes")
    tts_voice: str = os.getenv("TTS_VOICE", "es-MX-DaliaNeural")  # o es-MX-JorgeNeural
    tts_rate: str = os.getenv("TTS_RATE", "+0%")

    # Vision Settings
    camera_device: str = os.getenv("CAMERA_DEVICE", "/dev/video0")
    camera_width: int = int(os.getenv("CAMERA_WIDTH", "1920"))
    camera_height: int = int(os.getenv("CAMERA_HEIGHT", "1080"))

    # Tools Settings
    enable_tools: bool = os.getenv("ENABLE_TOOLS", "true").lower() in ("true", "1", "yes")
    auto_execute_safe_tools: bool = True

config = JarvisConfig()
