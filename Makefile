.PHONY: pytest
pytest:
	uv run pytest --cov=src/nornir_netbox --cov-report=term-missing -vs ${ARGS}

.PHONY: format
black:
	uv run ruff format --check .

.PHONY: ruff
pylama:
	uv run check .

.PHONY: mypy
mypy:
	uv run mypy .

.PHONY: tests
tests: format ruff mypy pytest
