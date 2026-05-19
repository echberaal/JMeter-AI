"""Stage 1 — Document Ingestion & Understanding pipeline."""

from __future__ import annotations

import time
from pathlib import Path

from config.logging_config import get_logger
from config.settings import get_settings
from jmeter_ai.agents.extraction_agent import ExtractionAgent
from jmeter_ai.core.schemas import ExtractionMetadata, Scenario
from jmeter_ai.document_processing.factory import DocumentLoaderFactory
from jmeter_ai.utils.file_utils import compute_file_hash, get_file_size
from jmeter_ai.utils.validators import validate_file_path

logger = get_logger(__name__)


class Stage1Pipeline:
    """Orchestrates the full Stage 1: file → ParsedDocument → Scenario."""

    def __init__(self) -> None:
        self._factory = DocumentLoaderFactory()
        self._agent = ExtractionAgent()

    async def run(self, file_path: Path) -> Scenario:
        """Execute the Stage 1 pipeline end-to-end.

        Args:
            file_path: Path to the input document.

        Returns:
            A fully enriched Scenario object.

        Raises:
            FileNotFoundError: If the file does not exist.
            UnsupportedFormatError: If the file type is not supported.
            DocumentTooLargeError: If the file exceeds size limits.
            ExtractionRetryExhaustedError: If extraction fails after retries.
        """
        settings = get_settings()
        start_time = time.time()

        # Step 1: Validate
        logger.info("stage1_validate", file=str(file_path))
        validate_file_path(
            file_path,
            max_size_mb=settings.max_document_size_mb,
            allowed_extensions=settings.supported_formats_list,
        )

        # Step 2: Load document
        logger.info("stage1_load", file=str(file_path))
        loader = self._factory.get_loader(file_path)
        parsed_doc = await loader.load(file_path)
        logger.info(
            "stage1_loaded",
            sections=len(parsed_doc.sections),
            pages=parsed_doc.page_count,
            chars=len(parsed_doc.raw_text),
        )

        # Step 3: Extract with LLM
        logger.info("stage1_extract", source=parsed_doc.source_path)
        scenario = await self._agent.extract(parsed_doc)

        # Step 4: Enrich metadata
        elapsed_ms = int((time.time() - start_time) * 1000)
        file_hash = await compute_file_hash(file_path)
        file_size = await get_file_size(file_path)

        scenario.extraction_metadata = ExtractionMetadata(
            source_file=str(file_path),
            source_file_hash=file_hash,
            file_type=parsed_doc.file_type,
            file_size_bytes=file_size,
            page_count=parsed_doc.page_count,
            extraction_duration_ms=elapsed_ms,
            llm_provider=settings.llm_provider.value,
            llm_model=settings.llm_model,
            prompt_version="1.0.0",
            overall_confidence=self._compute_overall_confidence(scenario),
            warnings=scenario.extraction_metadata.warnings if scenario.extraction_metadata else [],
            unresolved_questions=(
                scenario.extraction_metadata.unresolved_questions
                if scenario.extraction_metadata
                else []
            ),
        )

        logger.info(
            "stage1_complete",
            scenario_name=scenario.name,
            transactions=len(scenario.transactions),
            variables=len(scenario.global_variables),
            confidence=scenario.extraction_metadata.overall_confidence,
            elapsed_ms=elapsed_ms,
        )

        return scenario

    def _compute_overall_confidence(self, scenario: Scenario) -> float:
        """Compute weighted average confidence across all transactions and steps."""
        confidences: list[float] = []
        for txn in scenario.transactions:
            confidences.append(txn.confidence)
            for step in txn.steps:
                confidences.append(step.confidence)
        if not confidences:
            return 0.0
        return round(sum(confidences) / len(confidences), 3)
