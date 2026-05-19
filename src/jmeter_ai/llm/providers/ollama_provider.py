"""Ollama (local) LLM provider adapter."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from config.settings import Settings


def build_ollama_llm(settings: Settings) -> BaseChatModel:
    """Build a ChatOllama instance from application settings."""
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        num_predict=settings.llm_max_tokens,
        base_url=settings.ollama_base_url,
    )
