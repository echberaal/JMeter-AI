"""Extraction agent — transforms a parsed document into a structured Scenario."""

from __future__ import annotations

import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from config.logging_config import get_logger
from config.settings import get_settings
from jmeter_ai.agents.base_agent import AbstractAgent
from jmeter_ai.core.exceptions import (
    ExtractionRetryExhaustedError,
    ExtractionValidationError,
    LLMInvocationError,
)
from jmeter_ai.core.schemas import ParsedDocument, Scenario
from jmeter_ai.llm.factory import get_llm

logger = get_logger(__name__)


class ExtractionAgent(AbstractAgent):
    """Agent that extracts a Scenario from a ParsedDocument using an LLM."""

    def __init__(self) -> None:
        llm = get_llm()
        super().__init__(llm)
        self._structured_llm = llm.with_structured_output(Scenario)

    async def invoke(self, *args: Any, **kwargs: Any) -> Scenario:
        """Invoke the extraction agent (delegates to extract)."""
        parsed_doc: ParsedDocument = args[0] if args else kwargs["parsed_doc"]
        return await self.extract(parsed_doc)

    async def extract(self, parsed_doc: ParsedDocument) -> Scenario:
        """Extract a Scenario from a parsed document.

        Args:
            parsed_doc: The parsed document to extract from.

        Returns:
            A validated Scenario object.

        Raises:
            ExtractionRetryExhaustedError: If all retries are exhausted.
            LLMInvocationError: If the LLM call fails unexpectedly.
        """
        settings = get_settings()
        max_retries = settings.extraction_max_retries

        if not self._prompt_template:
            self._prompt_template = await self._load_prompt("stage1_extraction.txt")

        file_metadata = (
            f"Source: {parsed_doc.source_path}\n"
            f"Type: {parsed_doc.file_type}\n"
            f"Pages: {parsed_doc.page_count}\n"
            f"Sections: {len(parsed_doc.sections)}"
        )

        prompt_text = self._prompt_template.format(
            document_text=parsed_doc.raw_text,
            file_metadata=file_metadata,
        )

        last_error: Exception | None = None

        for attempt in range(max_retries + 1):
            logger.info(
                "extraction_attempt",
                attempt=attempt + 1,
                max_retries=max_retries,
                source=parsed_doc.source_path,
            )

            try:
                start_ms = int(time.time() * 1000)

                messages: list[Any] = []
                if attempt == 0:
                    messages = [
                        SystemMessage(content="You are a QA automation expert."),
                        HumanMessage(content=prompt_text),
                    ]
                else:
                    error_feedback = (
                        f"Your previous response failed validation with this error:\n"
                        f"{last_error}\n\n"
                        f"Please fix the issues and try again. "
                        f"Ensure all referenced_variables exist in global_variables "
                        f"or are produced by prior steps."
                    )
                    messages = [
                        SystemMessage(content="You are a QA automation expert."),
                        HumanMessage(content=prompt_text),
                        HumanMessage(content=error_feedback),
                    ]

                result = await self._structured_llm.ainvoke(messages)
                elapsed_ms = int(time.time() * 1000) - start_ms

                if not isinstance(result, Scenario):
                    raise ExtractionValidationError(  # noqa: TRY301
                        "LLM did not return a valid Scenario object"
                    )

                logger.info(
                    "extraction_success",
                    attempt=attempt + 1,
                    elapsed_ms=elapsed_ms,
                    transactions=len(result.transactions),
                )
                return result

            except ValidationError as exc:
                last_error = exc
                logger.warning(
                    "extraction_validation_error",
                    attempt=attempt + 1,
                    error=str(exc),
                )
            except ExtractionValidationError as exc:
                last_error = exc
                logger.warning(
                    "extraction_validation_error",
                    attempt=attempt + 1,
                    error=str(exc),
                )
            except Exception as exc:
                raise LLMInvocationError(f"LLM invocation failed: {exc}") from exc

        raise ExtractionRetryExhaustedError(
            f"Extraction failed after {max_retries + 1} attempts. Last error: {last_error}"
        )
