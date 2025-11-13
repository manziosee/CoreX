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

dev: ## Start development environment
	docker-compose up -d postgres redis rabbitmq
	uvicorn app.main:app --reload

setup: ## Initial setup
	cp .env.example .env
	docker-compose up -d