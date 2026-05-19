"""OpenAI LLM provider adapter."""

from __future__ import annotations

import os

import httpx
from langchain_core.language_models import BaseChatModel

from config.settings import Settings
from jmeter_ai.core.exceptions import LLMConfigurationError


def build_openai_llm(settings: Settings) -> BaseChatModel:
    """Build a ChatOpenAI instance from application settings.

    Raises:
        LLMConfigurationError: If the OpenAI API key is not configured.
    """
    api_key = settings.openai_api_key.get_secret_value()
    if not api_key:
        raise LLMConfigurationError("OPENAI_API_KEY is required for the OpenAI provider")

    from langchain_openai import ChatOpenAI

    kwargs: dict[str, object] = {
        "model": settings.llm_model,
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
        "timeout": settings.llm_timeout_seconds,
        "max_retries": settings.llm_max_retries,
        "api_key": api_key,
    }
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url

    # Corporate proxy SSL: use custom CA bundle if SSL_CERT_FILE is set
    ssl_cert_file = os.environ.get("SSL_CERT_FILE", "")
    if ssl_cert_file and os.path.isfile(ssl_cert_file):
        kwargs["http_client"] = httpx.Client(verify=ssl_cert_file)
        kwargs["http_async_client"] = httpx.AsyncClient(verify=ssl_cert_file)

    return ChatOpenAI(**kwargs)
