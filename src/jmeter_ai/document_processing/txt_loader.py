"""Plain-text document loader."""

from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar

import aiofiles

from jmeter_ai.core.schemas import DocumentSection, ParsedDocument
from jmeter_ai.document_processing.base import AbstractDocumentLoader


class TxtLoader(AbstractDocumentLoader):
    """Loads .txt files, splitting into sections by headings or blank lines."""

    supported_extensions: ClassVar[set[str]] = {"txt"}

    async def load(self, path: Path) -> ParsedDocument:
        """Load a plain text file and parse sections."""
        await self._validate_file(path)

        async with aiofiles.open(path, encoding="utf-8") as f:
            raw_text = await f.read()

        sections = self._split_sections(raw_text)

        return ParsedDocument(
            source_path=str(path),
            file_type="txt",
            raw_text=raw_text,
            sections=sections,
            metadata={"encoding": "utf-8"},
            page_count=1,
        )

    def _split_sections(self, text: str) -> list[DocumentSection]:
        """Split text into sections by markdown-style headings or double newlines."""
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        sections: list[DocumentSection] = []
        last_end = 0
        last_heading = ""
        last_level = 1
        found_headings = False

        for match in heading_pattern.finditer(text):
            found_headings = True
            # Content before this heading
            content = text[last_end : match.start()].strip()
            if content:
                sections.append(
                    DocumentSection(
                        heading=last_heading,
                        content=content,
                        level=last_level,
                        type="body",
                    )
                )
            last_heading = match.group(2).strip()
            last_level = len(match.group(1))
            last_end = match.end()

        if found_headings:
            # Remaining content after last heading
            remaining = text[last_end:].strip()
            if remaining:
                sections.append(
                    DocumentSection(
                        heading=last_heading,
                        content=remaining,
                        level=last_level,
                        type="body",
                    )
                )
        else:
            # No headings found — split by double newline
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
            for para in paragraphs:
                sections.append(DocumentSection(heading="", content=para, level=1, type="body"))

        return sections
