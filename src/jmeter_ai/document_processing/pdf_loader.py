"""PDF document loader using pypdf."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import ClassVar

from jmeter_ai.core.exceptions import DocumentParseError
from jmeter_ai.core.schemas import DocumentSection, ParsedDocument
from jmeter_ai.document_processing.base import AbstractDocumentLoader


class PdfLoader(AbstractDocumentLoader):
    """Loads PDF files, extracting text page by page."""

    supported_extensions: ClassVar[set[str]] = {"pdf"}

    async def load(self, path: Path) -> ParsedDocument:
        """Load a PDF file and extract text from each page."""
        await self._validate_file(path)
        return await asyncio.to_thread(self._load_sync, path)

    def _load_sync(self, path: Path) -> ParsedDocument:
        """Synchronous PDF loading (pypdf is not async)."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
        except Exception as exc:
            raise DocumentParseError(f"Failed to parse PDF: {exc}") from exc

        pages_text: list[str] = []
        sections: list[DocumentSection] = []

        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages_text.append(text)
            if text.strip():
                sections.append(
                    DocumentSection(
                        heading=f"Page {i}",
                        content=text.strip(),
                        level=1,
                        type="page",
                    )
                )

        raw_text = "\n\n".join(pages_text)
        return ParsedDocument(
            source_path=str(path),
            file_type="pdf",
            raw_text=raw_text,
            sections=sections,
            metadata={"page_count": len(reader.pages)},
            page_count=len(reader.pages),
        )
