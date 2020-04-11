.PHONY: pytest
pytest:
	poetry run pytest --cov=nornir_netbox --cov-report=term-missing -vs ${ARGS}

.PHONY: black
black:
	poetry run black --check .

.PHONY: pylama
pylama:
	poetry run pylama .

.PHONY: mypy
mypy:
	poetry run mypy .

.PHONY: tests
tests: black pylama mypy pytest
