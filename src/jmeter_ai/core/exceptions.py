"""Custom exception hierarchy for JMeter AI Assistant."""

from __future__ import annotations


class JMeterAIError(Exception):
    """Base exception for all JMeter AI errors."""

    def __init__(self, message: str = "", *, details: str = "") -> None:
        self.details = details
        super().__init__(message)


# --- Document Processing ---


class DocumentProcessingError(JMeterAIError):
    """Base for document processing errors."""


class UnsupportedFormatError(DocumentProcessingError):
    """Raised when a document format is not supported."""


class DocumentTooLargeError(DocumentProcessingError):
    """Raised when a document exceeds the maximum allowed size."""


class DocumentParseError(DocumentProcessingError):
    """Raised when a document cannot be parsed."""


# --- LLM ---


class LLMError(JMeterAIError):
    """Base for LLM-related errors."""


class LLMConfigurationError(LLMError):
    """Raised when an LLM provider is misconfigured."""


class LLMInvocationError(LLMError):
    """Raised when an LLM call fails."""


# --- Extraction ---


class ExtractionError(JMeterAIError):
    """Base for extraction errors."""


class ExtractionValidationError(ExtractionError):
    """Raised when extracted data fails validation."""


class ExtractionRetryExhaustedError(ExtractionError):
    """Raised when extraction retries are exhausted."""
