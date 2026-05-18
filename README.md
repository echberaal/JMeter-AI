# JMeter AI Assistant

An AI-powered JMeter scripting assistant that automatically generates, validates, and optimises Apache JMeter test plans from natural-language documents (PDF, DOCX, PPTX, TXT).

---

## Vision & Goals

Manual JMeter scripting is slow, error-prone, and requires deep expertise. This project replaces that workflow with an AI pipeline:

- **Document → JMX**: Upload a functional spec or test strategy and receive a production-ready `.jmx` file.
- **Multi-provider LLM support**: OpenAI, Anthropic Claude, Azure OpenAI, Google Gemini, or local Ollama.
- **MCP-native**: Exposes every JMeter element as a typed MCP tool consumable by Claude Desktop, Cursor, and other MCP clients.
- **5-stage pipeline**: Ingest → Validate → Script → Correlate → Report.
- **FastAPI bridge**: HTTP/WebSocket API for UI or CI/CD integration.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     JMeter AI Assistant                      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Stage 1        │  Document Ingestion & Extraction
│  INGESTION      │  PDF / DOCX / PPTX / TXT → Structured Scenario
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stage 2        │  Scenario Validation
│  VALIDATION     │  LLM validates completeness & coherence
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stage 3        │  JMX Script Generation
│  SCRIPTING      │  Structured scenario → .jmx via MCP tools
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stage 4        │  Correlation & Dynamic Data
│  CORRELATION    │  Auto-detect & patch dynamic tokens
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stage 5        │  Execution & Reporting
│  REPORTING      │  Run JMeter, parse JTL, generate report
└─────────────────┘
```

---

## Folder Structure

```
jmeter-ai-assistant/
├── config/          # Settings, LLM config, logging, prompt templates
├── docs/            # Architecture docs, stage guides, MCP tool catalogue
├── src/jmeter_ai/   # Core Python package
│   ├── core/        # Schemas, exceptions, constants
│   ├── llm/         # LLM factory + provider adapters
│   ├── document_processing/  # Loaders for PDF, DOCX, PPTX, TXT
│   ├── agents/      # LangChain agents per stage
│   ├── mcp_server/  # FastMCP server + tool registry
│   ├── jmx/         # JMX builder, serializer, element models, templates
│   ├── execution/   # JMeter runner + JTL parser
│   ├── correlation/ # Dynamic token detection & patching
│   ├── api/         # FastAPI HTTP + WebSocket bridge
│   ├── stages/      # Orchestration of the 5-stage pipeline
│   └── utils/       # File, XML, and validation utilities
├── tests/           # Unit, integration, fixtures
├── jmeter_plugin/   # Optional Java plugin (Maven project)
├── scripts/         # Dev & CI shell scripts
├── docker/          # Dockerfile + docker-compose
└── output/          # Generated .jmx files (git-ignored)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangChain, LangGraph |
| MCP server | FastMCP |
| API | FastAPI + uvicorn |
| Schemas | Pydantic v2 + pydantic-settings |
| XML generation | lxml |
| Document parsing | pypdf, python-docx, python-pptx, unstructured |
| Logging | structlog |
| Testing | pytest + pytest-asyncio + pytest-cov |
| Lint / Format | ruff + black |
| Type checking | mypy (strict) |
| Package manager | uv |
| LLM providers | OpenAI, Anthropic, Azure OpenAI, Google Gemini, Ollama |

---

## Quickstart

```bash
# 1. Install dependencies
uv sync

# 2. Configure environment
cp config/.env.example config/.env
# Edit config/.env and add your API keys

# 3. Run the MCP server
make mcp

# 4. Run the FastAPI bridge (separate terminal)
make api

# 5. Run tests
make test
```

---

## Stage Roadmap

| Stage | Name | Description |
|---|---|---|
| 1 | **Ingestion** | Parse uploaded documents; extract endpoints, headers, payloads, auth info, and performance targets into a structured `TestScenario`. |
| 2 | **Validation** | LLM-powered review of the extracted scenario. Flags missing fields, ambiguous auth, or conflicting load targets before scripting begins. |
| 3 | **Scripting** | LangChain agent calls MCP tools to assemble a complete `.jmx` tree: thread groups, HTTP samplers, assertions, extractors, CSV datasets. |
| 4 | **Correlation** | Static + LLM analysis of the generated JMX to detect dynamic tokens (CSRF, session IDs, OAuth flows). Auto-inserts regex/JSON extractors and variables. |
| 5 | **Reporting** | Invokes JMeter in non-GUI mode, captures the JTL, parses results, and produces an HTML + JSON performance report. |

---

## Configuration

All configuration is managed via environment variables. See [`config/.env.example`](config/.env.example) for the full list.

Key variables:

```bash
LLM_PROVIDER=openai       # openai | anthropic | ollama | azure_openai | google
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
JMETER_HOME=/opt/jmeter
LOG_LEVEL=INFO
```

---

## Development Workflow

```bash
make install     # Install all dependencies (including dev)
make lint        # Run ruff linter
make format      # Run black formatter
make typecheck   # Run mypy
make test        # Run full test suite
make test-unit   # Run unit tests only
make clean       # Remove build artefacts
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Commit with conventional commits: `feat:`, `fix:`, `docs:`, `test:`.
4. Ensure `make lint && make typecheck && make test` all pass.
5. Open a pull request.

---

## License

MIT — see [LICENSE](LICENSE).
