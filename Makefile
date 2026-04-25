.PHONY: install-dev up down migrate api test lint typecheck

install-dev:
	pip install -e ".[dev]"

up:
	docker compose up -d

down:
	docker compose down

migrate:
	alembic upgrade head

api:
	uvicorn arb_finder.api.app:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy src
