"""Unit tests for the LLM factory and providers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from jmeter_ai.core.exceptions import LLMConfigurationError
from jmeter_ai.llm.factory import get_llm, reset_llm_cache


@pytest.fixture(autouse=True)
def _clear_cache():
    """Reset LLM cache before each test."""
    reset_llm_cache()
    yield
    reset_llm_cache()


class TestOpenAIProvider:
    def test_missing_api_key_raises(self):
        from config.settings import Settings

        settings = Settings(
            llm_provider="openai",  # type: ignore[arg-type]
            openai_api_key="",  # type: ignore[arg-type]
        )
        from jmeter_ai.llm.providers.openai_provider import build_openai_llm

        with pytest.raises(LLMConfigurationError, match="OPENAI_API_KEY"):
            build_openai_llm(settings)

    @patch("langchain_openai.ChatOpenAI")
    def test_builds_with_valid_key(self, mock_cls):
        from config.settings import Settings

        settings = Settings(
            llm_provider="openai",  # type: ignore[arg-type]
            openai_api_key="sk-test",  # type: ignore[arg-type]
            llm_model="gpt-4o-mini",
        )
        mock_cls.return_value = MagicMock()
        from jmeter_ai.llm.providers.openai_provider import build_openai_llm

        result = build_openai_llm(settings)
        assert result is not None
        mock_cls.assert_called_once()


class TestAnthropicProvider:
    def test_missing_api_key_raises(self):
        from config.settings import Settings

        settings = Settings(
            llm_provider="anthropic",  # type: ignore[arg-type]
            anthropic_api_key="",  # type: ignore[arg-type]
        )
        from jmeter_ai.llm.providers.anthropic_provider import build_anthropic_llm

        with pytest.raises(LLMConfigurationError, match="ANTHROPIC_API_KEY"):
            build_anthropic_llm(settings)

    @patch("langchain_anthropic.ChatAnthropic")
    def test_builds_with_valid_key(self, mock_cls):
        from config.settings import Settings

        settings = Settings(
            llm_provider="anthropic",  # type: ignore[arg-type]
            anthropic_api_key="sk-ant-test",  # type: ignore[arg-type]
            llm_model="claude-3-sonnet",
        )
        mock_cls.return_value = MagicMock()
        from jmeter_ai.llm.providers.anthropic_provider import build_anthropic_llm

        result = build_anthropic_llm(settings)
        assert result is not None


class TestOllamaProvider:
    @patch("langchain_ollama.ChatOllama")
    def test_builds_without_api_key(self, mock_cls):
        from config.settings import Settings

        settings = Settings(
            llm_provider="ollama",  # type: ignore[arg-type]
            llm_model="llama3",
            ollama_base_url="http://localhost:11434",
        )
        mock_cls.return_value = MagicMock()
        from jmeter_ai.llm.providers.ollama_provider import build_ollama_llm

        result = build_ollama_llm(settings)
        assert result is not None


class TestAzureOpenAIProvider:
    def test_missing_api_key_raises(self):
        from config.settings import Settings

        settings = Settings(
            llm_provider="azure_openai",  # type: ignore[arg-type]
            azure_openai_api_key="",  # type: ignore[arg-type]
            azure_openai_endpoint="https://test.openai.azure.com",
        )
        from jmeter_ai.llm.providers.azure_openai_provider import build_azure_openai_llm

        with pytest.raises(LLMConfigurationError, match="AZURE_OPENAI_API_KEY"):
            build_azure_openai_llm(settings)

    def test_missing_endpoint_raises(self):
        from config.settings import Settings

        settings = Settings(
            llm_provider="azure_openai",  # type: ignore[arg-type]
            azure_openai_api_key="test-key",  # type: ignore[arg-type]
            azure_openai_endpoint="",
        )
        from jmeter_ai.llm.providers.azure_openai_provider import build_azure_openai_llm

        with pytest.raises(LLMConfigurationError, match="AZURE_OPENAI_ENDPOINT"):
            build_azure_openai_llm(settings)


class TestGoogleProvider:
    def test_missing_api_key_raises(self):
        from config.settings import Settings

        settings = Settings(
            llm_provider="google",  # type: ignore[arg-type]
            google_api_key="",  # type: ignore[arg-type]
        )
        from jmeter_ai.llm.providers.google_provider import build_google_llm

        with pytest.raises(LLMConfigurationError, match="GOOGLE_API_KEY"):
            build_google_llm(settings)


class TestFactory:
    @patch("langchain_openai.ChatOpenAI")
    def test_get_llm_openai(self, mock_cls, monkeypatch):
        from config.settings import Settings

        settings = Settings(
            llm_provider="openai",  # type: ignore[arg-type]
            openai_api_key="sk-test",  # type: ignore[arg-type]
        )
        monkeypatch.setattr("config.settings.get_settings", lambda: settings)
        mock_cls.return_value = MagicMock()

        result = get_llm()
        assert result is not None
