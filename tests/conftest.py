"""Shared test fixtures for the JMeter AI Assistant."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure config imports work by setting env vars before anything else
os.environ.setdefault("LLM_PROVIDER", "openai")
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-unit-tests")


@pytest.fixture
def sample_txt_path() -> Path:
    """Path to the sample.txt fixture."""
    return Path(__file__).parent / "fixtures" / "sample_documents" / "sample.txt"


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Temporary output directory for test artifacts."""
    out = tmp_path / "output"
    out.mkdir()
    return out


@pytest.fixture
def mock_settings():
    """Mock settings with test defaults."""
    from config.settings import Settings

    return Settings(
        llm_provider="openai",  # type: ignore[arg-type]
        llm_model="gpt-4o-mini",
        llm_temperature=0.1,
        llm_max_tokens=4096,
        llm_timeout_seconds=30,
        llm_max_retries=1,
        openai_api_key="sk-test-key",  # type: ignore[arg-type]
        max_document_size_mb=20,
        supported_formats="pdf,docx,pptx,txt",
        extraction_max_retries=1,
        extraction_confidence_threshold=0.6,
        log_level="DEBUG",
        output_dir=Path("/tmp/test-output"),
        prompts_dir=Path(__file__).parent.parent / "config" / "prompts",
    )


@pytest.fixture
def mock_llm():
    """A mock LangChain BaseChatModel."""
    llm = MagicMock()
    llm.ainvoke = AsyncMock()
    llm.with_structured_output = MagicMock(return_value=llm)
    return llm


@pytest.fixture
def mock_scenario():
    """A minimal valid Scenario for testing."""
    from jmeter_ai.core.schemas import (
        Authentication,
        AuthenticationType,
        Environment,
        ExtractionMetadata,
        HttpMethod,
        Scenario,
        Step,
        Transaction,
        Variable,
        VariableSource,
    )

    return Scenario(
        name="Test Scenario",
        description="A test scenario",
        base_url="https://example.com",
        environment=Environment(name="staging"),
        authentication=Authentication(
            type=AuthenticationType.FORM_LOGIN,
            details={"login_url": "/auth/login"},
            confidence=0.9,
        ),
        global_variables=[
            Variable(
                name="username",
                description="Test user",
                example_value="testuser",
                source=VariableSource.CSV,
            ),
        ],
        transactions=[
            Transaction(
                order=1,
                name="Login",
                description="User login flow",
                steps=[
                    Step(
                        order=1,
                        name="Submit login",
                        method=HttpMethod.POST,
                        url_hint="/auth/login",
                        referenced_variables=["username"],
                        confidence=0.9,
                    ),
                ],
                confidence=0.9,
            ),
        ],
        extraction_metadata=ExtractionMetadata(
            source_file="test.txt",
            file_type="txt",
        ),
    )


@pytest.fixture
def patch_get_settings(mock_settings):
    """Patch get_settings to return mock_settings."""
    with patch("config.settings.get_settings", return_value=mock_settings):
        yield mock_settings
