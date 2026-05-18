from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config.settings import Settings


@dataclass
class OpenAIConfig:
    api_key: str
    model: str
    temperature: float
    max_tokens: int
    timeout: int
    max_retries: int
    base_url: str = ""


@dataclass
class AnthropicConfig:
    api_key: str
    model: str
    temperature: float
    max_tokens: int
    timeout: int
    max_retries: int


@dataclass
class OllamaConfig:
    base_url: str
    model: str
    temperature: float
    max_tokens: int
    timeout: int


@dataclass
class AzureOpenAIConfig:
    api_key: str
    endpoint: str
    api_version: str
    deployment: str
    model: str
    temperature: float
    max_tokens: int
    timeout: int
    max_retries: int


@dataclass
class GoogleConfig:
    api_key: str
    model: str
    temperature: float
    max_tokens: int
    timeout: int
    max_retries: int


ProviderConfig = OpenAIConfig | AnthropicConfig | OllamaConfig | AzureOpenAIConfig | GoogleConfig


def get_provider_config(settings: Settings) -> ProviderConfig:
    from config.settings import LLMProvider

    match settings.llm_provider:
        case LLMProvider.OPENAI:
            return OpenAIConfig(
                api_key=settings.openai_api_key.get_secret_value(),
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
                base_url=settings.openai_base_url,
            )
        case LLMProvider.ANTHROPIC:
            return AnthropicConfig(
                api_key=settings.anthropic_api_key.get_secret_value(),
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
            )
        case LLMProvider.OLLAMA:
            return OllamaConfig(
                base_url=settings.ollama_base_url,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout_seconds,
            )
        case LLMProvider.AZURE_OPENAI:
            return AzureOpenAIConfig(
                api_key=settings.azure_openai_api_key.get_secret_value(),
                endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
                deployment=settings.azure_openai_deployment,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
            )
        case LLMProvider.GOOGLE:
            return GoogleConfig(
                api_key=settings.google_api_key.get_secret_value(),
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
            )
