"""Pydantic v2 schemas for Stage 1 document processing and scenario extraction."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# --- Enums ---


class HttpMethod(StrEnum):
    """HTTP methods supported in test scenarios."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ActionType(StrEnum):
    """Types of user actions in a test scenario."""

    NAVIGATE = "NAVIGATE"
    FORM_SUBMIT = "FORM_SUBMIT"
    API_CALL = "API_CALL"
    SEARCH = "SEARCH"
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
    LOGOUT = "LOGOUT"
    OTHER = "OTHER"


class VariableSource(StrEnum):
    """Source of a variable value."""

    CSV = "CSV"
    UDV = "UDV"
    EXTRACTED = "EXTRACTED"
    USER_INPUT = "USER_INPUT"


class AuthenticationType(StrEnum):
    """Authentication mechanisms."""

    NONE = "NONE"
    BASIC = "BASIC"
    FORM_LOGIN = "FORM_LOGIN"
    OAUTH2 = "OAUTH2"
    JWT = "JWT"
    SSO = "SSO"
    CUSTOM = "CUSTOM"


# --- Document Models ---


class DocumentSection(BaseModel):
    """A logical section extracted from a document."""

    heading: str = ""
    content: str
    level: int = Field(default=1, ge=1)
    type: str = "body"


class ParsedDocument(BaseModel):
    """Result of document parsing before LLM extraction."""

    source_path: str
    file_type: str
    raw_text: str
    sections: list[DocumentSection] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    page_count: int = Field(default=1, ge=1)


# --- Scenario Models ---


class Variable(BaseModel):
    """A parameterizable variable in the scenario."""

    name: str
    description: str = ""
    example_value: str = ""
    source: VariableSource = VariableSource.UDV
    is_sensitive: bool = False
    referenced_in_steps: list[int] = Field(default_factory=list)


class RequestBody(BaseModel):
    """Body of an HTTP request."""

    type: str = Field(default="json", pattern=r"^(json|form|raw|multipart)$")
    content: str = ""
    fields: dict[str, str] = Field(default_factory=dict)


class Step(BaseModel):
    """A single HTTP request step in a transaction."""

    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order: int = Field(ge=1)
    name: str
    description: str = ""
    action_type: ActionType = ActionType.API_CALL
    method: HttpMethod = HttpMethod.GET
    url_hint: str = ""
    headers: dict[str, str] = Field(default_factory=dict)
    query_params: dict[str, str] = Field(default_factory=dict)
    body: RequestBody | None = None
    expected_outcome: str = ""
    expected_status_code: int = Field(default=200, ge=100, le=599)
    referenced_variables: list[str] = Field(default_factory=list)
    produces_variables: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    notes: str = ""

    @field_validator("confidence")
    @classmethod
    def _validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            msg = "confidence must be between 0.0 and 1.0"
            raise ValueError(msg)
        return v


class Transaction(BaseModel):
    """A logical group of steps (e.g., 'Login Flow')."""

    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order: int = Field(ge=1)
    name: str
    description: str = ""
    think_time_seconds: float = Field(default=1.0, ge=0.0)
    tags: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    steps: list[Step] = Field(default_factory=list)

    @field_validator("confidence")
    @classmethod
    def _validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            msg = "confidence must be between 0.0 and 1.0"
            raise ValueError(msg)
        return v


class Authentication(BaseModel):
    """Authentication details for the scenario."""

    type: AuthenticationType = AuthenticationType.NONE
    details: dict[str, str] = Field(default_factory=dict)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class Environment(BaseModel):
    """Target environment configuration."""

    name: str = "default"
    notes: str = ""


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process itself."""

    source_file: str
    source_file_hash: str = ""
    file_type: str
    file_size_bytes: int = 0
    page_count: int = 1
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    extraction_duration_ms: int = 0
    llm_provider: str = ""
    llm_model: str = ""
    prompt_version: str = ""
    overall_confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    retry_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    detected_languages: list[str] = Field(default_factory=list)


class Scenario(BaseModel):
    """Top-level scenario extracted from a document."""

    schema_version: str = Field(default="1.0.0")
    scenario_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    base_url: str = ""
    environment: Environment = Field(default_factory=Environment)
    authentication: Authentication = Field(default_factory=Authentication)
    global_variables: list[Variable] = Field(default_factory=list)
    transactions: list[Transaction] = Field(default_factory=list)
    extraction_metadata: ExtractionMetadata | None = None

    @model_validator(mode="after")
    def _validate_referenced_variables(self) -> Scenario:
        """Ensure referenced_variables in steps exist in global_variables."""
        known_names = {v.name for v in self.global_variables}
        produced_names: set[str] = set()
        for txn in self.transactions:
            for step in txn.steps:
                produced_names.update(step.produces_variables)

        all_known = known_names | produced_names
        for txn in self.transactions:
            for step in txn.steps:
                for ref in step.referenced_variables:
                    if ref not in all_known:
                        msg = (
                            f"Step '{step.name}' references variable '{ref}' "
                            f"which is not defined in global_variables or produced by a prior step"
                        )
                        raise ValueError(msg)
        return self
