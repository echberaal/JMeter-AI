"""LLM factory — single entrypoint to get a configured chat model."""

from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models import BaseChatModel

from config.settings import LLMProvider, get_settings


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """Return a cached LLM instance based on current settings."""
    settings = get_settings()

    match settings.llm_provider:
        case LLMProvider.OPENAI:
            from jmeter_ai.llm.providers.openai_provider import build_openai_llm

            return build_openai_llm(settings)
        case LLMProvider.ANTHROPIC:
            from jmeter_ai.llm.providers.anthropic_provider import build_anthropic_llm

            return build_anthropic_llm(settings)
        case LLMProvider.OLLAMA:
            from jmeter_ai.llm.providers.ollama_provider import build_ollama_llm

            return build_ollama_llm(settings)
        case LLMProvider.AZURE_OPENAI:
            from jmeter_ai.llm.providers.azure_openai_provider import build_azure_openai_llm

            return build_azure_openai_llm(settings)
        case LLMProvider.GOOGLE:
            from jmeter_ai.llm.providers.google_provider import build_google_llm

            return build_google_llm(settings)


def reset_llm_cache() -> None:
    """Clear the cached LLM instance. Useful in tests."""
    get_llm.cache_clear()
