"""Unit tests for document loaders."""

from __future__ import annotations

from pathlib import Path

import pytest

from jmeter_ai.core.exceptions import DocumentTooLargeError, UnsupportedFormatError
from jmeter_ai.document_processing.factory import DocumentLoaderFactory
from jmeter_ai.document_processing.txt_loader import TxtLoader


class TestTxtLoader:
    @pytest.fixture
    def loader(self) -> TxtLoader:
        return TxtLoader()

    @pytest.mark.asyncio
    async def test_load_sample_txt(self, loader: TxtLoader, sample_txt_path: Path):
        doc = await loader.load(sample_txt_path)
        assert doc.file_type == "txt"
        assert doc.raw_text
        assert len(doc.sections) > 0
        assert doc.page_count == 1

    @pytest.mark.asyncio
    async def test_load_nonexistent_file(self, loader: TxtLoader, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            await loader.load(tmp_path / "nonexistent.txt")

    @pytest.mark.asyncio
    async def test_sections_from_headings(self, loader: TxtLoader, tmp_path: Path):
        content = "# Heading 1\nContent 1\n\n## Heading 2\nContent 2\n"
        f = tmp_path / "headings.txt"
        f.write_text(content, encoding="utf-8")
        doc = await loader.load(f)
        assert any(s.heading == "Heading 1" for s in doc.sections)
        assert any(s.heading == "Heading 2" for s in doc.sections)

    @pytest.mark.asyncio
    async def test_sections_from_blank_lines(self, loader: TxtLoader, tmp_path: Path):
        content = "Paragraph one.\n\nParagraph two.\n\nParagraph three.\n"
        f = tmp_path / "paragraphs.txt"
        f.write_text(content, encoding="utf-8")
        doc = await loader.load(f)
        assert len(doc.sections) == 3

    @pytest.mark.asyncio
    async def test_unsupported_extension(self, loader: TxtLoader, tmp_path: Path):
        f = tmp_path / "file.xyz"
        f.write_text("data", encoding="utf-8")
        with pytest.raises(UnsupportedFormatError):
            await loader.load(f)


class TestDocumentLoaderFactory:
    def test_get_loader_txt(self, sample_txt_path: Path):
        loader = DocumentLoaderFactory.get_loader(sample_txt_path)
        assert isinstance(loader, TxtLoader)

    def test_get_loader_unsupported(self, tmp_path: Path):
        f = tmp_path / "file.xyz"
        f.write_text("data", encoding="utf-8")
        with pytest.raises(UnsupportedFormatError):
            DocumentLoaderFactory.get_loader(f)

    def test_registered_extensions(self):
        assert "txt" in DocumentLoaderFactory._registry
        assert "pdf" in DocumentLoaderFactory._registry
        assert "docx" in DocumentLoaderFactory._registry
        assert "pptx" in DocumentLoaderFactory._registry


class TestDocumentSizeLimits:
    @pytest.mark.asyncio
    async def test_file_too_large(self, tmp_path: Path, monkeypatch):
        """Files exceeding the size limit should raise DocumentTooLargeError."""
        f = tmp_path / "big.txt"
        f.write_text("x" * 1000, encoding="utf-8")

        class TinySettings:
            max_document_size_mb = 0  # 0 MB = 0 bytes limit

        monkeypatch.setattr(
            "jmeter_ai.document_processing.base.get_settings", lambda: TinySettings()
        )

        loader = TxtLoader()
        with pytest.raises(DocumentTooLargeError):
            await loader.load(f)
