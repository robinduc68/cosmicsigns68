# Cosmic Signs — developer entry points.
# Every target is safe to run from a clean checkout.

SHELL := /bin/bash
PNPM  := corepack pnpm
PY    := apps/api/.venv/bin/python
PIP   := $(HOME)/.local/bin/uv pip
API   := apps/api/.venv/bin

export DATABASE_URL ?= postgresql+asyncpg://cosmic:cosmic@localhost:5436/cosmic_signs

.DEFAULT_GOAL := help
.PHONY: help setup install-web install-api db-up db-down up down logs \
        dev dev-api dev-web migrate migration lint format typecheck test \
        test-api test-engine test-web clean

help: ## Show the available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: install-api install-web db-up migrate ## First-time setup: dependencies, database, migrations
	@echo "Ready. Run 'make dev'."

install-api: ## Create the Python venv and install backend dependencies
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	cd apps/api && uv venv --python 3.12 .venv
	cd apps/api && uv pip install -e ../../packages/astrology-engine
	cd apps/api && uv pip install fastapi "uvicorn[standard]" pydantic pydantic-settings \
		"sqlalchemy[asyncio]" asyncpg alembic structlog pytest pytest-asyncio httpx \
		ruff mypy aiosqlite greenlet

install-web: ## Install JavaScript dependencies
	$(PNPM) install

db-up: ## Start PostgreSQL
	docker compose up -d postgres
	@until docker exec cosmic_postgres pg_isready -U cosmic -d cosmic_signs >/dev/null 2>&1; \
		do sleep 1; done
	@echo "PostgreSQL is ready on port 5436."

db-down: ## Stop PostgreSQL
	docker compose stop postgres

up: ## Run the whole stack in Docker (web + api + db)
	docker compose --profile full up -d --build

down: ## Stop every container
	docker compose --profile full --profile cache down

logs: ## Follow container logs
	docker compose --profile full logs -f

dev: db-up ## Run API and web locally with hot reload
	@trap 'kill 0' EXIT; \
	(cd apps/api && ./.venv/bin/uvicorn app.main:app --reload --port 8100) & \
	$(PNPM) --filter @cosmic/web dev & \
	wait

dev-api: db-up ## Run only the API
	cd apps/api && ./.venv/bin/uvicorn app.main:app --reload --port 8100

dev-web: ## Run only the web app
	$(PNPM) --filter @cosmic/web dev

migrate: ## Apply database migrations
	cd apps/api && ./.venv/bin/alembic upgrade head

migration: ## Autogenerate a migration: make migration m="add table"
	cd apps/api && ./.venv/bin/alembic revision --autogenerate -m "$(m)"

lint: ## Lint everything
	$(PNPM) lint
	$(API)/ruff check apps/api/app apps/api/tests
	$(API)/ruff check packages/astrology-engine/src packages/astrology-engine/tests

format: ## Format everything
	$(PNPM) format
	$(API)/ruff format apps/api/app apps/api/tests
	$(API)/ruff format packages/astrology-engine/src packages/astrology-engine/tests

typecheck: ## Typecheck everything
	$(PNPM) typecheck
	cd apps/api && ./.venv/bin/mypy app
	cd packages/astrology-engine && ../../apps/api/.venv/bin/mypy src

test: test-engine test-api test-web ## Run every test suite

test-engine: ## Astrology engine tests
	cd packages/astrology-engine && ../../apps/api/.venv/bin/python -m pytest -q

test-api: ## Backend tests (SQLite, no Docker needed)
	cd apps/api && ./.venv/bin/python -m pytest -q

test-web: ## Frontend tests
	$(PNPM) --filter @cosmic/web test

clean: ## Remove build artefacts and caches
	rm -rf node_modules apps/web/.nuxt apps/web/.output \
		$$(find . -name __pycache__ -type d) .pytest_cache
