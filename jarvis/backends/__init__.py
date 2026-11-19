from .base import BaseLLMClient, LLMResponse, ToolCall
from .openai_client import OpenAICompatibleClient
from .gemini_client import GeminiClient

def get_llm_client(provider: str, api_key: str = "", base_url: str = "", model: str = "", temperature: float = 0.4) -> BaseLLMClient:
    provider = provider.lower()
    if provider == "gemini":
        return GeminiClient(api_key=api_key, model=model or "gemini-2.5-flash", temperature=temperature)
    elif provider in ("ollama", "lmstudio", "openai", "local"):
        return OpenAICompatibleClient(
            base_url=base_url or "http://localhost:11434/v1",
            api_key=api_key or "ollama",
            model=model or "llama3.2-vision",
            temperature=temperature
        )
    else:
        raise ValueError(f"Proveedor '{provider}' no soportado. Usa: gemini, ollama, lmstudio, o openai.")

__all__ = ["BaseLLMClient", "LLMResponse", "ToolCall", "OpenAICompatibleClient", "GeminiClient", "get_llm_client"]
