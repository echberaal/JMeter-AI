"""Document loader factory — routes files to the correct loader."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from jmeter_ai.core.exceptions import UnsupportedFormatError
from jmeter_ai.document_processing.base import AbstractDocumentLoader
from jmeter_ai.document_processing.docx_loader import DocxLoader
from jmeter_ai.document_processing.pdf_loader import PdfLoader
from jmeter_ai.document_processing.pptx_loader import PptxLoader
from jmeter_ai.document_processing.txt_loader import TxtLoader


class DocumentLoaderFactory:
    """Registry-based factory that returns the correct loader for a file."""

    _registry: ClassVar[dict[str, type[AbstractDocumentLoader]]] = {}

    @classmethod
    def register(cls, loader_cls: type[AbstractDocumentLoader]) -> type[AbstractDocumentLoader]:
        """Register a loader class for its supported extensions."""
        for ext in loader_cls.supported_extensions:
            cls._registry[ext] = loader_cls
        return loader_cls

    @classmethod
    def get_loader(cls, path: Path) -> AbstractDocumentLoader:
        """Return an instantiated loader for the given file path.

        Raises:
            UnsupportedFormatError: If no loader is registered for the extension.
        """
        ext = path.suffix.lower().lstrip(".")
        loader_cls = cls._registry.get(ext)
        if loader_cls is None:
            supported = sorted(cls._registry.keys())
            raise UnsupportedFormatError(f"No loader for '.{ext}'. Supported: {supported}")
        return loader_cls()


# Auto-register all built-in loaders
DocumentLoaderFactory.register(TxtLoader)
DocumentLoaderFactory.register(PdfLoader)
DocumentLoaderFactory.register(DocxLoader)
DocumentLoaderFactory.register(PptxLoader)
