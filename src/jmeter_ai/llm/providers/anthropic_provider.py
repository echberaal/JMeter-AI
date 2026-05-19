"""Anthropic LLM provider adapter."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from config.settings import Settings
from jmeter_ai.core.exceptions import LLMConfigurationError


def build_anthropic_llm(settings: Settings) -> BaseChatModel:
    """Build a ChatAnthropic instance from application settings.

    Raises:
        LLMConfigurationError: If the Anthropic API key is not configured.
    """
    api_key = settings.anthropic_api_key.get_secret_value()
    if not api_key:
        raise LLMConfigurationError("ANTHROPIC_API_KEY is required for the Anthropic provider")

    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        timeout=float(settings.llm_timeout_seconds),
        max_retries=settings.llm_max_retries,
        api_key=api_key,
    )
