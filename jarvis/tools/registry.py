"""
JARVIS Assistant - Sistema de Registro de Herramientas (Tool Calling)
Convierte funciones de Python con docstrings y anotaciones de tipo
directamente a esquemas de Function Calling compatibles con OpenAI, Ollama y Gemini.
"""

import inspect
import json
from typing import Any, Callable, Dict, List, get_type_hints

TYPE_MAPPING = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, func: Callable) -> Callable:
        """Decorador para registrar una función de Python como una herramienta invocable por JARVIS."""
        name = func.__name__
        doc = inspect.getdoc(func) or f"Ejecuta la acción {name}"
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_type = type_hints.get(param_name, str)
            json_type = TYPE_MAPPING.get(param_type, "string")

            properties[param_name] = {
                "type": json_type,
                "description": f"Parámetro {param_name}",
            }

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": doc,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

        self._tools[name] = func
        self._schemas.append(schema)
        return func

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Devuelve los esquemas de todas las herramientas registradas."""
        return self._schemas

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Ejecuta una herramienta registrada por su nombre pasando los argumentos."""
        if tool_name not in self._tools:
            return f"Error: La herramienta '{tool_name}' no existe."
        try:
            return self._tools[tool_name](**arguments)
        except Exception as e:
            return f"Error al ejecutar '{tool_name}': {str(e)}"

# Instancia global del registro
tools = ToolRegistry()
tool = tools.register
