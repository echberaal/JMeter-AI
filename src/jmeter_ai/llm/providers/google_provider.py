"""Google Gemini LLM provider adapter."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from config.settings import Settings
from jmeter_ai.core.exceptions import LLMConfigurationError


def build_google_llm(settings: Settings) -> BaseChatModel:
    """Build a ChatGoogleGenerativeAI instance from application settings.

    Raises:
        LLMConfigurationError: If GOOGLE_API_KEY is not configured.
    """
    api_key = settings.google_api_key.get_secret_value()
    if not api_key:
        raise LLMConfigurationError("GOOGLE_API_KEY is required for the Google provider")

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_tokens,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
        google_api_key=api_key,
    )
