"""Abstract base for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel

from config.settings import Settings


class AbstractLLMProvider(ABC):
    """Base class that all LLM provider adapters extend."""

    @abstractmethod
    def build(self, settings: Settings) -> BaseChatModel:
        """Construct and return a configured LangChain chat model."""
