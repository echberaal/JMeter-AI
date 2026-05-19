"""Integration tests for Stage 1 pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jmeter_ai.core.schemas import (
    HttpMethod,
    Scenario,
    Step,
    Transaction,
    Variable,
    VariableSource,
)


def _make_settings():
    from config.settings import Settings

    return Settings(
        llm_provider="openai",  # type: ignore[arg-type]
        openai_api_key="sk-test",  # type: ignore[arg-type]
        extraction_max_retries=1,
        log_level="DEBUG",
        prompts_dir=Path(__file__).parent.parent.parent / "config" / "prompts",
        max_document_size_mb=20,
        supported_formats="pdf,docx,pptx,txt",
    )


@pytest.fixture
def valid_scenario() -> Scenario:
    """A realistic scenario that the mock LLM will return."""
    return Scenario(
        name="E-Commerce Login and Search",
        description="Login, search, and logout flow",
        base_url="https://shop.example.com",
        global_variables=[
            Variable(name="username", source=VariableSource.CSV),
            Variable(name="password", source=VariableSource.CSV, is_sensitive=True),
            Variable(name="search_term", source=VariableSource.CSV),
        ],
        transactions=[
            Transaction(
                order=1,
                name="Login",
                steps=[
                    Step(
                        order=1,
                        name="Navigate to homepage",
                        method=HttpMethod.GET,
                        url_hint="/",
                    ),
                    Step(
                        order=2,
                        name="Submit login",
                        method=HttpMethod.POST,
                        url_hint="/auth/login",
                        referenced_variables=["username", "password"],
                    ),
                ],
                confidence=0.9,
            ),
            Transaction(
                order=2,
                name="Search Products",
                steps=[
                    Step(
                        order=1,
                        name="Search",
                        method=HttpMethod.GET,
                        url_hint="/api/products",
                        referenced_variables=["search_term"],
                    ),
                ],
                confidence=0.85,
            ),
        ],
    )


class TestStage1Pipeline:
    @pytest.mark.asyncio
    async def test_end_to_end_with_sample_txt(self, sample_txt_path, valid_scenario):
        """Full pipeline with mocked LLM on real sample.txt fixture."""
        settings = _make_settings()

        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.ainvoke = AsyncMock(return_value=valid_scenario)
        mock_llm.with_structured_output = MagicMock(return_value=mock_structured)

        with (
            patch("config.settings.get_settings", return_value=settings),
            patch("jmeter_ai.agents.extraction_agent.get_llm", return_value=mock_llm),
        ):
            from jmeter_ai.stages.stage1_ingestion import Stage1Pipeline

            pipeline = Stage1Pipeline()
            result = await pipeline.run(sample_txt_path)

        # Verify result
        assert isinstance(result, Scenario)
        assert result.name == "E-Commerce Login and Search"
        assert len(result.transactions) == 2
        assert len(result.global_variables) == 3

        # Verify metadata was enriched
        meta = result.extraction_metadata
        assert meta is not None
        assert meta.source_file == str(sample_txt_path)
        assert meta.file_type == "txt"
        assert meta.file_size_bytes > 0
        assert meta.source_file_hash  # non-empty
        assert meta.llm_provider == "openai"
        assert meta.llm_model == "gpt-4o-mini"
        assert meta.extraction_duration_ms >= 0

    @pytest.mark.asyncio
    async def test_nonexistent_file_raises(self, tmp_path):
        """Pipeline raises FileNotFoundError for missing files."""
        settings = _make_settings()

        with patch("config.settings.get_settings", return_value=settings):
            from jmeter_ai.stages.stage1_ingestion import Stage1Pipeline

            pipeline = Stage1Pipeline()
            with pytest.raises(FileNotFoundError):
                await pipeline.run(tmp_path / "nonexistent.txt")
