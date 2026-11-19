"""
Herramientas de manejo de archivos para JARVIS.
"""

import os
from pathlib import Path
from .registry import tool

@tool
def read_file_content(path: str) -> str:
    """Lee y devuelve el contenido de un archivo de texto en el disco."""
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Error: El archivo '{path}' no existe."
    if not p.is_file():
        return f"Error: '{path}' no es un archivo regular."
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return content[:8000] + ("\n... [Contenido truncado a 8000 caracteres]" if len(content) > 8000 else "")
    except Exception as e:
        return f"Error leyendo archivo: {str(e)}"

@tool
def list_directory(path: str = ".") -> str:
    """Lista los archivos y carpetas dentro de la ruta especificada."""
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Error: La ruta '{path}' no existe."
    if not p.is_dir():
        return f"Error: '{path}' no es un directorio."
    try:
        items = os.listdir(p)
        return "\n".join(sorted(items)[:100])
    except Exception as e:
        return f"Error listando directorio: {str(e)}"
