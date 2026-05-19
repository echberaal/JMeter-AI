"""Unit tests for the ExtractionAgent."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jmeter_ai.core.exceptions import (
    ExtractionRetryExhaustedError,
    ExtractionValidationError,
    LLMInvocationError,
)
from jmeter_ai.core.schemas import (
    HttpMethod,
    ParsedDocument,
    Scenario,
    Step,
    Transaction,
)


@pytest.fixture
def parsed_doc() -> ParsedDocument:
    return ParsedDocument(
        source_path="/tmp/test.txt",
        file_type="txt",
        raw_text="User logs in at /login with POST",
        sections=[],
        page_count=1,
    )


@pytest.fixture
def valid_scenario() -> Scenario:
    return Scenario(
        name="Test Scenario",
        description="Test",
        base_url="https://example.com",
        transactions=[
            Transaction(
                order=1,
                name="Login",
                steps=[
                    Step(order=1, name="Login POST", method=HttpMethod.POST, url_hint="/login"),
                ],
            )
        ],
    )


def _make_settings():
    from config.settings import Settings

    return Settings(
        llm_provider="openai",  # type: ignore[arg-type]
        openai_api_key="sk-test",  # type: ignore[arg-type]
        extraction_max_retries=2,
        log_level="DEBUG",
        prompts_dir=Path(__file__).parent.parent.parent / "config" / "prompts",
    )


class TestExtractionAgent:
    @pytest.mark.asyncio
    async def test_happy_path(self, parsed_doc, valid_scenario):
        """Successful extraction returns a Scenario."""
        settings = _make_settings()
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.ainvoke = AsyncMock(return_value=valid_scenario)
        mock_llm.with_structured_output = MagicMock(return_value=mock_structured)

        with (
            patch("config.settings.get_settings", return_value=settings),
            patch("jmeter_ai.agents.extraction_agent.get_llm", return_value=mock_llm),
        ):
            from jmeter_ai.agents.extraction_agent import ExtractionAgent

            agent = ExtractionAgent()
            result = await agent.extract(parsed_doc)

        assert isinstance(result, Scenario)
        assert result.name == "Test Scenario"
        mock_structured.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_on_validation_error(self, parsed_doc, valid_scenario):
        """Agent retries when LLM returns invalid data, then succeeds."""
        settings = _make_settings()
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.ainvoke = AsyncMock(
            side_effect=[
                ExtractionValidationError("bad data"),
                valid_scenario,
            ]
        )
        mock_llm.with_structured_output = MagicMock(return_value=mock_structured)

        with (
            patch("config.settings.get_settings", return_value=settings),
            patch("jmeter_ai.agents.extraction_agent.get_llm", return_value=mock_llm),
        ):
            from jmeter_ai.agents.extraction_agent import ExtractionAgent

            agent = ExtractionAgent()
            result = await agent.extract(parsed_doc)

        assert isinstance(result, Scenario)
        assert mock_structured.ainvoke.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self, parsed_doc):
        """Agent raises ExtractionRetryExhaustedError after max retries."""
        settings = _make_settings()
        settings = settings.model_copy(update={"extraction_max_retries": 1})

        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.ainvoke = AsyncMock(side_effect=ExtractionValidationError("always fails"))
        mock_llm.with_structured_output = MagicMock(return_value=mock_structured)

        with (
            patch("config.settings.get_settings", return_value=settings),
            patch("jmeter_ai.agents.extraction_agent.get_llm", return_value=mock_llm),
        ):
            from jmeter_ai.agents.extraction_agent import ExtractionAgent

            agent = ExtractionAgent()
            with pytest.raises(ExtractionRetryExhaustedError):
                await agent.extract(parsed_doc)

    @pytest.mark.asyncio
    async def test_llm_invocation_error(self, parsed_doc):
        """Unexpected LLM errors raise LLMInvocationError."""
        settings = _make_settings()
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.ainvoke = AsyncMock(side_effect=RuntimeError("connection failed"))
        mock_llm.with_structured_output = MagicMock(return_value=mock_structured)

        with (
            patch("config.settings.get_settings", return_value=settings),
            patch("jmeter_ai.agents.extraction_agent.get_llm", return_value=mock_llm),
        ):
            from jmeter_ai.agents.extraction_agent import ExtractionAgent

            agent = ExtractionAgent()
            with pytest.raises(LLMInvocationError, match="connection failed"):
                await agent.extract(parsed_doc)
