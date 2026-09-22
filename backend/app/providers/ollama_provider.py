import json
from typing import AsyncGenerator, Dict, Any, List
import httpx
from app.providers.base import BaseLLMProvider
from app.config import settings
from app.observability.logging import logger

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip('/')
        self.model = model or settings.OLLAMA_MODEL

    @property
    def name(self) -> str:
        return "ollama"

    async def health_check(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    model_found = any(self.model in m for m in models)
                    return {
                        "status": "healthy" if model_found else "warning",
                        "connected": True,
                        "model": self.model,
                        "model_available": model_found,
                        "available_models": models
                    }
                return {"status": "unhealthy", "connected": True, "error": f"Status {res.status_code}"}
        except Exception as e:
            return {"status": "disconnected", "connected": False, "error": str(e), "model": self.model}

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        full_text = ""
        async for chunk in self.stream(messages, **kwargs):
            full_text += chunk
        return full_text

    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", 0.3)
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        err_msg = await response.aread()
                        raise RuntimeError(f"Ollama error ({response.status_code}): {err_msg.decode('utf-8')}")

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError as e:
            logger.error(f"Ollama connection refused at {self.base_url}: {e}")
            raise ConnectionError(f"Cannot connect to local Ollama daemon at {self.base_url}. Ensure Ollama is running.") from e
        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            raise e
