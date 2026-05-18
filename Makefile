.PHONY: install dev test test-unit test-integration lint format typecheck mcp api clean docker-build docker-up docker-down

UV := uv
SRC := src/jmeter_ai
TESTS := tests

install:
	$(UV) sync --all-extras

dev:
	$(UV) sync --all-extras
	pre-commit install

test:
	$(UV) run pytest $(TESTS) -v

test-unit:
	$(UV) run pytest $(TESTS)/unit -v

test-integration:
	$(UV) run pytest $(TESTS)/integration -v

lint:
	$(UV) run ruff check $(SRC) $(TESTS)

format:
	$(UV) run black $(SRC) $(TESTS)
	$(UV) run ruff check --fix $(SRC) $(TESTS)

typecheck:
	$(UV) run mypy $(SRC)

mcp:
	$(UV) run python -m jmeter_ai.mcp_server.server

api:
	$(UV) run uvicorn jmeter_ai.api.main:app --host 0.0.0.0 --port 8000 --reload

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f .coverage coverage.xml

docker-build:
	docker build -t jmeter-ai-assistant -f docker/Dockerfile .

docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down
