COMPOSE = docker compose

.PHONY: help env up down restart build logs ps test test-e2e lint migrate shell clean

help:
	@echo "Available targets:"
	@echo "  make up        - create .env if needed and start the stack"
	@echo "  make down      - stop containers"
	@echo "  make restart   - restart containers"
	@echo "  make build     - build images"
	@echo "  make logs      - follow logs"
	@echo "  make ps        - show container status"
	@echo "  make test      - run tests inside the api container"
	@echo "  make test-e2e  - run e2e test against the running stack"
	@echo "  make lint      - run ruff inside the api container"
	@echo "  make migrate   - run alembic migrations"
	@echo "  make shell     - open shell in the api container"
	@echo "  make clean     - stop containers and remove volumes"

env:
	@test -f .env || cp .env.example .env

up: env
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

restart: down up

build: env
	$(COMPOSE) build

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

test: up
	$(COMPOSE) exec -T api pytest

test-e2e: up
	$(COMPOSE) exec -T -e RUN_E2E=1 api pytest tests/e2e

lint: up
	$(COMPOSE) exec -T api ruff check .

migrate: up
	$(COMPOSE) exec -T api alembic upgrade head

shell: up
	$(COMPOSE) exec api sh

clean:
	$(COMPOSE) down -v
