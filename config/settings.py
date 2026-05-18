from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=["./config/.env", "./.env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM
    llm_provider: LLMProvider = LLMProvider.OPENAI
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 3

    # OpenAI
    openai_api_key: SecretStr = SecretStr("")
    openai_base_url: str = ""

    # Anthropic
    anthropic_api_key: SecretStr = SecretStr("")

    # Azure OpenAI
    azure_openai_api_key: SecretStr = SecretStr("")
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment: str = ""

    # Google
    google_api_key: SecretStr = SecretStr("")

    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # Document processing
    max_document_size_mb: int = 20
    supported_formats: str = "pdf,docx,pptx,txt"

    # Extraction
    extraction_max_retries: int = 2
    extraction_confidence_threshold: float = 0.6

    # MCP server
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8765

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # JMeter
    jmeter_home: Path = Path("/opt/jmeter")

    # App
    log_level: str = "INFO"
    output_dir: Path = Path("./output")
    prompts_dir: Path = Path("./config/prompts")

    @property
    def supported_formats_list(self) -> list[str]:
        return [fmt.strip() for fmt in self.supported_formats.split(",")]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
