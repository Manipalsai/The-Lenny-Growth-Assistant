from typing import Tuple
from app.providers.base import BaseLLMProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import CloudProvider
from app.config import settings
from app.observability.logging import logger

class ProviderFactory:
    @staticmethod
    def get_provider(provider_override: str = None) -> BaseLLMProvider:
        choice = (provider_override or settings.LLM_PROVIDER).lower()

        if choice == "anthropic":
            return CloudProvider(provider_type="anthropic")
        elif choice == "openai":
            return CloudProvider(provider_type="openai")
        elif choice == "ollama":
            return OllamaProvider()
        else:
            logger.warning(f"Unknown provider '{choice}', defaulting to Ollama.")
            return OllamaProvider()

    @staticmethod
    def get_fallback_provider() -> BaseLLMProvider:
        fallback_choice = settings.FALLBACK_PROVIDER.lower()
        if fallback_choice == "anthropic":
            return CloudProvider(provider_type="anthropic")
        return CloudProvider(provider_type="openai")

provider_factory = ProviderFactory()
