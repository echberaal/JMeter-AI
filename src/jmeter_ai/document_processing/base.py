"""Abstract base class for document loaders."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from config.settings import get_settings
from jmeter_ai.core.exceptions import (
    DocumentTooLargeError,
    UnsupportedFormatError,
)
from jmeter_ai.core.schemas import ParsedDocument


class AbstractDocumentLoader(ABC):
    """Base class for all document loaders."""

    supported_extensions: ClassVar[set[str]]

    @abstractmethod
    async def load(self, path: Path) -> ParsedDocument:
        """Load and parse a document into a ParsedDocument."""

    async def _validate_file(self, path: Path) -> None:
        """Validate that a file exists, has a supported extension, and is within size limits.

        Raises:
            FileNotFoundError: If the file does not exist.
            UnsupportedFormatError: If the file extension is not supported.
            DocumentTooLargeError: If the file exceeds the max size.
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        ext = path.suffix.lower().lstrip(".")
        if ext not in self.supported_extensions:
            raise UnsupportedFormatError(
                f"Unsupported extension '.{ext}'. Supported: {self.supported_extensions}"
            )

        settings = get_settings()
        max_bytes = settings.max_document_size_mb * 1024 * 1024
        file_size = path.stat().st_size
        if file_size > max_bytes:
            raise DocumentTooLargeError(
                f"File size {file_size} bytes exceeds maximum {max_bytes} bytes"
            )
