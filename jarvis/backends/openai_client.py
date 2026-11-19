"""
JARVIS Assistant - Conector OpenAI / Ollama / LM Studio (Compatible con cualquier servidor OpenAI)
"""

import json
import base64
from typing import Any, Dict, List, Optional
import httpx

from .base import BaseLLMClient, LLMResponse, ToolCall

class OpenAICompatibleClient(BaseLLMClient):
    def __init__(self, base_url: str = "http://localhost:11434/v1", api_key: str = "ollama", model: str = "llama3.2-vision", temperature: float = 0.4):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "not-needed"
        self.model = model
        self.temperature = temperature

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        image_bytes: Optional[bytes] = None
    ) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Preparar copia de mensajes para inyectar imagen si está disponible
        formatted_messages = []
        for m in messages:
            formatted_messages.append({"role": m["role"], "content": m["content"]})

        if image_bytes and formatted_messages:
            # Inyectar imagen en el último mensaje de usuario
            last_msg = formatted_messages[-1]
            if last_msg["role"] == "user":
                b64_img = base64.b64encode(image_bytes).decode("utf-8")
                img_data_url = f"data:image/jpeg;base64,{b64_img}"
                
                # Si el contenido era texto simple, convertir a array multimodal
                if isinstance(last_msg["content"], str):
                    last_msg["content"] = [
                        {"type": "text", "text": last_msg["content"]},
                        {"type": "image_url", "image_url": {"url": img_data_url}}
                    ]

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.temperature
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        with httpx.Client(timeout=90.0, trust_env=False) as client:
            resp = client.post(url, headers=headers, json=payload)
            # Si el modelo no soporta tool calling (como moondream/llava), reintentar sin tools
            if resp.status_code == 400 and "tool" in resp.text.lower() and "tools" in payload:
                payload_no_tools = dict(payload)
                del payload_no_tools["tools"]
                payload_no_tools.pop("tool_choice", None)
                resp = client.post(url, headers=headers, json=payload_no_tools)
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]["message"]
        content = choice.get("content", "")

        parsed_tool_calls: List[ToolCall] = []
        if "tool_calls" in choice and choice["tool_calls"]:
            for tc in choice["tool_calls"]:
                try:
                    fn = tc["function"]
                    args = json.loads(fn["arguments"]) if isinstance(fn["arguments"], str) else fn["arguments"]
                    parsed_tool_calls.append(ToolCall(
                        id=tc.get("id", "call_default"),
                        name=fn["name"],
                        arguments=args
                    ))
                except Exception as e:
                    print(f"[!] Error parseando tool call: {e}")

        return LLMResponse(
            content=content,
            tool_calls=parsed_tool_calls,
            raw=data
        )
