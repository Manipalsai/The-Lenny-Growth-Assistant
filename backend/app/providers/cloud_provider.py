import json
from typing import AsyncGenerator, Dict, Any, List
import httpx
from app.providers.base import BaseLLMProvider
from app.config import settings
from app.observability.logging import logger

class CloudProvider(BaseLLMProvider):
    def __init__(self, provider_type: str = "openai"):
        self.provider_type = provider_type.lower()
        if self.provider_type == "anthropic":
            self.api_key = settings.ANTHROPIC_API_KEY
            self.model = settings.ANTHROPIC_MODEL
        else:
            self.provider_type = "openai"
            self.api_key = settings.OPENAI_API_KEY
            self.model = settings.OPENAI_MODEL

    @property
    def name(self) -> str:
        return self.provider_type

    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "status": "unconfigured",
                "connected": False,
                "error": f"Missing {self.provider_type.upper()}_API_KEY",
                "model": self.model
            }
        return {
            "status": "configured",
            "connected": True,
            "provider": self.provider_type,
            "model": self.model
        }

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        full_text = ""
        async for chunk in self.stream(messages, **kwargs):
            full_text += chunk
        return full_text

    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise ValueError(f"{self.provider_type.upper()}_API_KEY is not configured in environment.")

        if self.provider_type == "anthropic":
            async for chunk in self._stream_anthropic(messages, **kwargs):
                yield chunk
        else:
            async for chunk in self._stream_openai(messages, **kwargs):
                yield chunk

    async def _stream_openai(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": kwargs.get("temperature", 0.3),
            "max_tokens": kwargs.get("max_tokens", 2500)
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", "https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_msg = await response.aread()
                    raise RuntimeError(f"OpenAI API error ({response.status_code}): {err_msg.decode('utf-8')}")

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            yield delta
                    except json.JSONDecodeError:
                        continue

    async def _stream_anthropic(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        # Convert standard messages to Anthropic format (extract system prompt if present)
        system_prompt = ""
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "system": system_prompt,
            "max_tokens": kwargs.get("max_tokens", 2500),
            "stream": True,
            "temperature": kwargs.get("temperature", 0.3)
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", "https://api.anthropic.com/v1/messages", headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_msg = await response.aread()
                    raise RuntimeError(f"Anthropic API error ({response.status_code}): {err_msg.decode('utf-8')}")

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    try:
                        data = json.loads(line[6:].strip())
                        if data.get("type") == "content_block_delta":
                            text = data.get("delta", {}).get("text", "")
                            if text:
                                yield text
                    except json.JSONDecodeError:
                        continue
