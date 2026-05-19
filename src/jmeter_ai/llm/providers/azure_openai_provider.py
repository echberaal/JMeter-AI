"""Azure OpenAI LLM provider adapter."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from config.settings import Settings
from jmeter_ai.core.exceptions import LLMConfigurationError


def build_azure_openai_llm(settings: Settings) -> BaseChatModel:
    """Build an AzureChatOpenAI instance from application settings.

    Raises:
        LLMConfigurationError: If required Azure OpenAI fields are missing.
    """
    api_key = settings.azure_openai_api_key.get_secret_value()
    if not api_key:
        raise LLMConfigurationError(
            "AZURE_OPENAI_API_KEY is required for the Azure OpenAI provider"
        )
    if not settings.azure_openai_endpoint:
        raise LLMConfigurationError(
            "AZURE_OPENAI_ENDPOINT is required for the Azure OpenAI provider"
        )

    from langchain_openai import AzureChatOpenAI

    return AzureChatOpenAI(
        azure_deployment=settings.azure_openai_deployment,
        api_version=settings.azure_openai_api_version,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=api_key,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )
