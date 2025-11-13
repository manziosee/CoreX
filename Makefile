.PHONY: help build up down logs test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

test: ## Run tests
	pytest

clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

dev: ## Start development environment (local PostgreSQL)
	python3 setup_db.py
	python3 manage_db.py upgrade
	uvicorn app.main:app --reload

dev-docker: ## Start development with Docker services only
	docker-compose -f docker-compose.local.yml up -d

dev-full: ## Start full development environment with Docker PostgreSQL
	docker-compose up -d postgres redis rabbitmq
	uvicorn app.main:app --reload

setup: ## Initial setup
	cp .env.example .env
	python3 setup_db.py
	docker-compose up -d

db-setup: ## Setup database and migrations
	python3 manage_db.py setup

db-migrate: ## Create new migration (usage: make db-migrate MESSAGE="your message")
	python3 manage_db.py migrate "$(MESSAGE)"

db-upgrade: ## Upgrade database to latest migration
	python3 manage_db.py upgrade

db-history: ## Show migration history
	python3 manage_db.py history

postman-update: ## Update Postman collection from API
	bash -c "source venv/bin/activate && python3 update_postman.py"

docs-db: ## Generate database documentation
	echo "📊 Database documentation available at docs/DATABASE.md"