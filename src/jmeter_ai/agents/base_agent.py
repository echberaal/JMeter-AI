"""Abstract base for LangChain-based agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import aiofiles
from langchain_core.language_models import BaseChatModel

from config.settings import get_settings


class AbstractAgent(ABC):
    """Base class for all AI agents in the pipeline."""

    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm
        self._prompt_template: str = ""

    async def _load_prompt(self, name: str) -> str:
        """Load a prompt template from the prompts directory.

        Args:
            name: Filename of the prompt (e.g., 'stage1_extraction.txt').

        Returns:
            The prompt template string.
        """
        settings = get_settings()
        prompt_path = Path(settings.prompts_dir) / name
        async with aiofiles.open(prompt_path, encoding="utf-8") as f:
            content: str = await f.read()
            return content

    @abstractmethod
    async def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent's main task."""
