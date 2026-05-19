"""Unit tests for core Pydantic schemas."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from jmeter_ai.core.schemas import (
    DocumentSection,
    ExtractionMetadata,
    HttpMethod,
    ParsedDocument,
    RequestBody,
    Scenario,
    Step,
    Transaction,
    Variable,
    VariableSource,
)


class TestVariable:
    def test_create_minimal(self):
        v = Variable(name="token")
        assert v.name == "token"
        assert v.source == VariableSource.UDV
        assert v.is_sensitive is False

    def test_create_sensitive(self):
        v = Variable(name="password", is_sensitive=True, source=VariableSource.CSV)
        assert v.is_sensitive is True
        assert v.source == VariableSource.CSV


class TestStep:
    def test_create_valid(self):
        s = Step(order=1, name="Login", method=HttpMethod.POST, url_hint="/login")
        assert s.order == 1
        assert s.method == HttpMethod.POST
        assert s.step_id  # auto-generated UUID

    def test_order_must_be_positive(self):
        with pytest.raises(ValidationError):
            Step(order=0, name="Bad")

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            Step(order=1, name="Bad", confidence=1.5)
        with pytest.raises(ValidationError):
            Step(order=1, name="Bad", confidence=-0.1)

    def test_auto_generated_step_id(self):
        s = Step(order=1, name="Test")
        uuid.UUID(s.step_id)  # Should not raise

    def test_request_body(self):
        s = Step(
            order=1,
            name="Post",
            method=HttpMethod.POST,
            body=RequestBody(type="json", content='{"key": "val"}'),
        )
        assert s.body is not None
        assert s.body.type == "json"


class TestTransaction:
    def test_create_valid(self):
        t = Transaction(order=1, name="Login Flow", steps=[])
        assert t.order == 1
        assert t.confidence == 0.8

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            Transaction(order=1, name="Bad", confidence=2.0)


class TestScenario:
    def test_create_minimal(self):
        s = Scenario(name="Test")
        assert s.schema_version == "1.0.0"
        assert s.scenario_id  # auto-generated

    def test_auto_generated_scenario_id(self):
        s = Scenario(name="Test")
        uuid.UUID(s.scenario_id)  # Should not raise

    def test_referenced_variable_validation_passes(self):
        """Steps referencing known global variables should pass."""
        s = Scenario(
            name="Test",
            global_variables=[Variable(name="user")],
            transactions=[
                Transaction(
                    order=1,
                    name="T1",
                    steps=[
                        Step(order=1, name="S1", referenced_variables=["user"]),
                    ],
                )
            ],
        )
        assert len(s.transactions) == 1

    def test_referenced_variable_validation_fails(self):
        """Steps referencing unknown variables should fail."""
        with pytest.raises(ValidationError, match="not defined"):
            Scenario(
                name="Test",
                global_variables=[],
                transactions=[
                    Transaction(
                        order=1,
                        name="T1",
                        steps=[
                            Step(order=1, name="S1", referenced_variables=["unknown_var"]),
                        ],
                    )
                ],
            )

    def test_produces_variables_are_valid_references(self):
        """Variables produced by a step can be referenced by later steps."""
        s = Scenario(
            name="Test",
            global_variables=[],
            transactions=[
                Transaction(
                    order=1,
                    name="T1",
                    steps=[
                        Step(order=1, name="S1", produces_variables=["token"]),
                        Step(order=2, name="S2", referenced_variables=["token"]),
                    ],
                )
            ],
        )
        assert len(s.transactions[0].steps) == 2


class TestParsedDocument:
    def test_create(self):
        doc = ParsedDocument(
            source_path="/tmp/test.txt",
            file_type="txt",
            raw_text="hello world",
            sections=[DocumentSection(content="hello world")],
        )
        assert doc.page_count == 1
        assert len(doc.sections) == 1


class TestExtractionMetadata:
    def test_defaults(self):
        meta = ExtractionMetadata(source_file="test.txt", file_type="txt")
        assert meta.overall_confidence == 0.8
        assert meta.retry_count == 0
