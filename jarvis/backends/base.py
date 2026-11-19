"""
JARVIS Assistant - Interfaz Base para Motores de Inteligencia Artificial
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class LLMResponse:
    content: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    raw: Any = None

class BaseLLMClient(ABC):
    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        image_bytes: Optional[bytes] = None
    ) -> LLMResponse:
        """Envía el historial de mensajes, herramientas e imagen opcional al modelo."""
        pass
