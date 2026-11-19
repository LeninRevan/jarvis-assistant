"""
JARVIS Assistant - Conector Nativo Google Gemini (Cloud API)
Soporta visión directa (inlineData) y declaración de herramientas (Function Calling).
"""

import json
import base64
from typing import Any, Dict, List, Optional
import httpx

from .base import BaseLLMClient, LLMResponse, ToolCall

class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", temperature: float = 0.4):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    def _convert_tools_to_gemini(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convierte esquemas de OpenAI a la especificación de Gemini."""
        declarations = []
        for t in tools:
            fn = t.get("function", {})
            declarations.append({
                "name": fn.get("name"),
                "description": fn.get("description"),
                "parameters": fn.get("parameters")
            })
        return [{"functionDeclarations": declarations}]

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        image_bytes: Optional[bytes] = None
    ) -> LLMResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # Mapear historial al formato de Gemini (contents)
        contents = []
        system_instruction = None

        for m in messages:
            role = m["role"]
            content = m["content"]
            if role == "system":
                system_instruction = {"parts": [{"text": str(content)}]}
                continue

            gemini_role = "user" if role == "user" else "model"
            parts: List[Dict[str, Any]] = []

            if isinstance(content, str):
                parts.append({"text": content})
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append({"text": item.get("text", "")})

            contents.append({"role": gemini_role, "parts": parts})

        # Inyectar imagen al último turno de usuario si existe
        if image_bytes and contents:
            b64_img = base64.b64encode(image_bytes).decode("utf-8")
            contents[-1]["parts"].append({
                "inlineData": {
                    "mimeType": "image/jpeg",
                    "data": b64_img
                }
            })

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 2048
            }
        }

        if system_instruction:
            payload["systemInstruction"] = system_instruction

        if tools:
            payload["tools"] = self._convert_tools_to_gemini(tools)

        with httpx.Client(timeout=90.0, trust_env=False) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return LLMResponse(content="[!] No se recibió respuesta del modelo.")

        first_cand = candidates[0].get("content", {})
        parts = first_cand.get("parts", [])

        text_content = ""
        tool_calls: List[ToolCall] = []

        for p in parts:
            if "text" in p:
                text_content += p["text"]
            elif "functionCall" in p:
                fc = p["functionCall"]
                tool_calls.append(ToolCall(
                    id=f"gemini_{fc.get('name')}",
                    name=fc.get("name", ""),
                    arguments=fc.get("args", {})
                ))

        return LLMResponse(
            content=text_content.strip() if text_content else None,
            tool_calls=tool_calls,
            raw=data
        )
