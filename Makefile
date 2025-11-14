# CoreX Banking System - Makefile
.PHONY: help setup dev dev-docker dev-full test build up down logs clean deploy

# Default target
help:
	@echo "🏦 CoreX Banking System - Available Commands"
	@echo "============================================="
	@echo "📦 Setup & Development:"
	@echo "  make setup          - Initial project setup"
	@echo "  make dev            - Start local development"
	@echo "  make dev-docker     - Start with Docker services"
	@echo "  make dev-full       - Full Docker development"
	@echo ""
	@echo "🐳 Docker Operations:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View service logs"
	@echo "  make clean          - Clean Docker resources"
	@echo ""
	@echo "🗄️  Database Operations:"
	@echo "  make db-setup       - Setup database"
	@echo "  make db-migrate     - Create migration"
	@echo "  make db-upgrade     - Apply migrations"
	@echo "  make db-reset       - Reset database"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-auth      - Test authentication"
	@echo "  make test-coverage  - Run tests with coverage"
	@echo ""
	@echo "🚀 Deployment:"
	@echo "  make deploy         - Deploy to Fly.io"
	@echo "  make deploy-prod    - Production deployment"

# Setup
setup:
	@echo "🔧 Setting up CoreX Banking System..."
	cp .env.example .env || true
	python3 -m venv venv || true
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Setup complete! Run 'make dev' to start development"

# Development
dev:
	@echo "🚀 Starting local development..."
	./venv/bin/python setup_db.py
	./venv/bin/python manage_db.py upgrade
	./venv/bin/python create_test_users.py
	./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-docker:
	@echo "🐳 Starting development with Docker services..."
	docker-compose -f docker-compose.local.yml up -d
	./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-full:
	@echo "🐳 Starting full Docker development..."
	docker-compose up -d

# Docker operations
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

up:
	@echo "🚀 Starting all services..."
	docker-compose up -d

down:
	@echo "🛑 Stopping all services..."
	docker-compose down

logs:
	@echo "📋 Viewing service logs..."
	docker-compose logs -f

clean:
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f

# Database operations
db-setup:
	@echo "🗄️  Setting up database..."
	./venv/bin/python setup_db.py
	./venv/bin/python manage_db.py upgrade

db-migrate:
	@echo "📝 Creating database migration..."
	@read -p "Migration message: " msg; \
	./venv/bin/python create_migration.py "$$msg"

db-upgrade:
	@echo "⬆️  Applying database migrations..."
	./venv/bin/python manage_db.py upgrade

db-reset:
	@echo "🔄 Resetting database..."
	./venv/bin/python manage_db.py downgrade base
	./venv/bin/python manage_db.py upgrade
	./venv/bin/python create_test_users.py

# Testing
test:
	@echo "🧪 Running all tests..."
	./venv/bin/pytest -v

test-auth:
	@echo "🔐 Testing authentication..."
	./venv/bin/python test_auth_endpoints.py

test-coverage:
	@echo "📊 Running tests with coverage..."
	./venv/bin/pytest --cov=app --cov-report=html

# Deployment
deploy:
	@echo "🚀 Deploying to Fly.io..."
	./deploy.sh

deploy-prod:
	@echo "🏭 Production deployment..."
	docker-compose -f docker-compose.prod.yml up -d

# Utilities
postman-update:
	@echo "📦 Updating Postman collection..."
	./venv/bin/python update_postman.py

docs-db:
	@echo "📚 Opening database documentation..."
	@echo "Database docs: docs/DATABASE.md"

status:
	@echo "📊 System Status:"
	@echo "=================="
	@curl -s http://localhost:8000/health | jq . || echo "❌ API not running"
	@docker-compose ps || echo "❌ Docker not running"