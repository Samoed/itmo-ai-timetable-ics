.DEFAULT_GOAL := all
DIRS = src/
pdm = pdm run
mypy = mypy

.PHONY: install
install:
	pdm install -d
	pre-commit install --install-hooks

.PHONY: format
format:
	pre-commit run
	$(pdm) ruff format $(DIRS)
	$(pdm) ruff check $(DIRS)
	$(pdm) mypy $(DIRS)


.PHONY: database
database:
	docker compose up database -d

.PHONY: test
test:
	$(pdm) pytest --cov=src --cov-report=html

.PHONY: migrate
migrate:
	@read -p "Enter migration message: " message; \
	$(pdm) alembic revision --autogenerate -m "$$message"

.PHONY: downgrade
downgrade:
	$(pdm) alembic downgrade -1

.PHONY: upgrade
upgrade:
	$(pdm) alembic upgrade +1

.PHONY: upgrade-offline
upgrade-offline:
	$(pdm) alembic upgrade head --sql

.PHONY: all
all: format export-dependencies
