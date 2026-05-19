"""File utility functions."""

from __future__ import annotations

import hashlib
from pathlib import Path

import aiofiles


async def compute_file_hash(path: Path) -> str:
    """Compute SHA-256 hash of a file.

    Args:
        path: Path to the file.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    sha256 = hashlib.sha256()
    async with aiofiles.open(path, mode="rb") as f:
        while True:
            chunk = await f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


async def get_file_size(path: Path) -> int:
    """Get file size in bytes.

    Args:
        path: Path to the file.

    Returns:
        File size in bytes.
    """
    return path.stat().st_size


def detect_file_type(path: Path) -> str:
    """Detect file type from extension.

    Args:
        path: Path to the file.

    Returns:
        One of: "pdf", "docx", "pptx", "txt".

    Raises:
        ValueError: If extension is not recognized.
    """
    ext = path.suffix.lower().lstrip(".")
    if ext in ("pdf", "docx", "pptx", "txt"):
        return ext
    msg = f"Unrecognized file extension: .{ext}"
    raise ValueError(msg)
