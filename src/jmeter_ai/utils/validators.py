"""Input validation utilities."""

from __future__ import annotations

from pathlib import Path

from jmeter_ai.core.exceptions import (
    DocumentTooLargeError,
    UnsupportedFormatError,
)


def validate_file_path(
    path: Path,
    max_size_mb: int,
    allowed_extensions: list[str],
) -> None:
    """Validate that a file path is usable for document processing.

    Args:
        path: The file path to validate.
        max_size_mb: Maximum allowed file size in megabytes.
        allowed_extensions: List of allowed file extensions (without dots).

    Raises:
        FileNotFoundError: If the file does not exist.
        UnsupportedFormatError: If the extension is not allowed.
        DocumentTooLargeError: If the file exceeds the size limit.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower().lstrip(".")
    if ext not in allowed_extensions:
        raise UnsupportedFormatError(f"Unsupported format '.{ext}'. Allowed: {allowed_extensions}")

    max_bytes = max_size_mb * 1024 * 1024
    file_size = path.stat().st_size
    if file_size > max_bytes:
        raise DocumentTooLargeError(
            f"File is {file_size} bytes, exceeds limit of {max_bytes} bytes ({max_size_mb} MB)"
        )
