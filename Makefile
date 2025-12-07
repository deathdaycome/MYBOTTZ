# ============================================
# Enterprise CRM - Makefile
# ============================================

.PHONY: help install start stop restart logs health test migrate shell clean build deploy

# Default target
.DEFAULT_GOAL := help

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help: ## Show this help message
	@echo "$(CYAN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║         Enterprise CRM - Development Commands             ║$(NC)"
	@echo "$(CYAN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================
# INSTALLATION & SETUP
# ============================================

install: ## Install Python dependencies
	@echo "$(CYAN)[INFO]$(NC) Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "$(GREEN)[✓]$(NC) Dependencies installed"

setup-env: ## Create .env file from example
	@if [ ! -f .env ]; then \
		echo "$(CYAN)[INFO]$(NC) Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "$(GREEN)[✓]$(NC) .env created. Please update with your values."; \
	else \
		echo "$(YELLOW)[!]$(NC) .env already exists"; \
	fi

init: setup-env install ## Initialize project (first time setup)
	@echo "$(GREEN)[✓]$(NC) Project initialized"

# ============================================
# DOCKER OPERATIONS
# ============================================

build: ## Build Docker images
	@echo "$(CYAN)[INFO]$(NC) Building Docker images..."
	docker-compose build
	@echo "$(GREEN)[✓]$(NC) Build complete"

start: ## Start all services with enterprise script
	@echo "$(CYAN)[INFO]$(NC) Starting Enterprise CRM..."
	./scripts/start_enterprise.sh

start-simple: ## Start services without health checks
	@echo "$(CYAN)[INFO]$(NC) Starting services..."
	docker-compose up -d
	@echo "$(GREEN)[✓]$(NC) Services started"

stop: ## Stop all services
	@echo "$(CYAN)[INFO]$(NC) Stopping services..."
	docker-compose down
	@echo "$(GREEN)[✓]$(NC) Services stopped"

restart: stop start ## Restart all services

restart-app: ## Restart only the FastAPI app
	@echo "$(CYAN)[INFO]$(NC) Restarting app..."
	docker-compose restart app
	@echo "$(GREEN)[✓]$(NC) App restarted"

ps: ## Show running containers
	docker-compose ps

# ============================================
# LOGS & MONITORING
# ============================================

logs: ## Show logs from all services
	docker-compose logs -f

logs-app: ## Show logs from FastAPI app
	docker-compose logs -f app

logs-celery: ## Show logs from Celery worker
	docker-compose logs -f celery-worker

logs-db: ## Show logs from PostgreSQL
	docker-compose logs -f postgres

logs-redis: ## Show logs from Redis
	docker-compose logs -f redis

health: ## Check health of all services
	@python3 scripts/quick_health_check.py

# ============================================
# DATABASE OPERATIONS
# ============================================

migrate: ## Run database migrations
	@echo "$(CYAN)[INFO]$(NC) Running migrations..."
	docker-compose run --rm app alembic upgrade head
	@echo "$(GREEN)[✓]$(NC) Migrations complete"

migrate-create: ## Create new migration (usage: make migrate-create MSG="description")
	@if [ -z "$(MSG)" ]; then \
		echo "$(RED)[✗]$(NC) Please provide message: make migrate-create MSG=\"your message\""; \
		exit 1; \
	fi
	@echo "$(CYAN)[INFO]$(NC) Creating migration: $(MSG)"
	docker-compose run --rm app alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)[✓]$(NC) Migration created"

migrate-downgrade: ## Downgrade one migration
	@echo "$(YELLOW)[!]$(NC) Downgrading migration..."
	docker-compose run --rm app alembic downgrade -1
	@echo "$(GREEN)[✓]$(NC) Downgrade complete"

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U crm_user crm_db

db-reset: ## Reset database (WARNING: destroys all data!)
	@echo "$(RED)[!]$(NC) This will DELETE ALL DATA. Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	@echo "$(CYAN)[INFO]$(NC) Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres
	@sleep 5
	docker-compose run --rm app alembic upgrade head
	@echo "$(GREEN)[✓]$(NC) Database reset complete"

# ============================================
# SHELL ACCESS
# ============================================

shell: ## Open shell in app container
	docker-compose exec app bash

shell-redis: ## Open Redis CLI
	docker-compose exec redis redis-cli

python-shell: ## Open Python shell with app context
	docker-compose exec app python3

# ============================================
# TESTING
# ============================================

test: ## Run all tests
	@echo "$(CYAN)[INFO]$(NC) Running tests..."
	python3 scripts/test_enterprise_setup.py

test-health: ## Quick health check
	@python3 scripts/quick_health_check.py

test-api: ## Test API endpoints
	@echo "$(CYAN)[INFO]$(NC) Testing API..."
	curl -s http://localhost:8000/health | python3 -m json.tool

# ============================================
# DEVELOPMENT
# ============================================

dev: ## Start in development mode (with auto-reload)
	@echo "$(CYAN)[INFO]$(NC) Starting development server..."
	docker-compose up app celery-worker celery-beat flower postgres redis

dev-local: ## Run FastAPI locally (no Docker)
	@echo "$(CYAN)[INFO]$(NC) Starting local development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint: ## Run code linters
	@echo "$(CYAN)[INFO]$(NC) Running linters..."
	flake8 app/
	black --check app/
	mypy app/

format: ## Format code with black
	@echo "$(CYAN)[INFO]$(NC) Formatting code..."
	black app/
	@echo "$(GREEN)[✓]$(NC) Code formatted"

# ============================================
# CELERY OPERATIONS
# ============================================

celery-worker: ## Start Celery worker (foreground)
	celery -A app.core.celery_app worker -l info

celery-beat: ## Start Celery beat scheduler (foreground)
	celery -A app.core.celery_app beat -l info

celery-flower: ## Open Celery Flower monitoring
	@echo "$(CYAN)[INFO]$(NC) Opening Flower at http://localhost:5555"
	@open http://localhost:5555 || xdg-open http://localhost:5555 || echo "Please open http://localhost:5555"

# ============================================
# MONITORING
# ============================================

prometheus: ## Open Prometheus
	@echo "$(CYAN)[INFO]$(NC) Opening Prometheus at http://localhost:9091"
	@open http://localhost:9091 || xdg-open http://localhost:9091 || echo "Please open http://localhost:9091"

grafana: ## Open Grafana
	@echo "$(CYAN)[INFO]$(NC) Opening Grafana at http://localhost:3000"
	@echo "$(YELLOW)[!]$(NC) Default credentials: admin/admin"
	@open http://localhost:3000 || xdg-open http://localhost:3000 || echo "Please open http://localhost:3000"

metrics: ## Show Prometheus metrics
	@curl -s http://localhost:8000/metrics

# ============================================
# DOCUMENTATION
# ============================================

docs: ## Open API documentation
	@echo "$(CYAN)[INFO]$(NC) Opening API docs at http://localhost:8000/docs"
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Please open http://localhost:8000/docs"

# ============================================
# CLEANUP
# ============================================

clean: ## Clean up cache and temporary files
	@echo "$(CYAN)[INFO]$(NC) Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)[✓]$(NC) Cleanup complete"

clean-docker: ## Remove all Docker containers and volumes (WARNING!)
	@echo "$(RED)[!]$(NC) This will DELETE ALL Docker data. Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	@echo "$(CYAN)[INFO]$(NC) Cleaning Docker..."
	docker-compose down -v --remove-orphans
	@echo "$(GREEN)[✓]$(NC) Docker cleanup complete"

# ============================================
# PRODUCTION DEPLOYMENT
# ============================================

deploy-check: ## Check if ready for deployment
	@echo "$(CYAN)[INFO]$(NC) Checking deployment readiness..."
	@echo "  [ ] .env configured"
	@echo "  [ ] Database migrations up to date"
	@echo "  [ ] Tests passing"
	@echo "  [ ] Security settings configured"
	@echo ""
	@echo "$(YELLOW)[!]$(NC) Manual checklist - verify each item above"

prod-build: ## Build for production
	@echo "$(CYAN)[INFO]$(NC) Building for production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
	@echo "$(GREEN)[✓]$(NC) Production build complete"

# ============================================
# UTILITY
# ============================================

ports: ## Show which ports are in use
	@echo "$(CYAN)[INFO]$(NC) Checking ports..."
	@echo "FastAPI:        8000"
	@lsof -i :8000 || echo "  Not in use"
	@echo "PostgreSQL:     5432"
	@lsof -i :5432 || echo "  Not in use"
	@echo "Redis:          6379"
	@lsof -i :6379 || echo "  Not in use"
	@echo "Flower:         5555"
	@lsof -i :5555 || echo "  Not in use"
	@echo "Prometheus:     9091"
	@lsof -i :9091 || echo "  Not in use"
	@echo "Grafana:        3000"
	@lsof -i :3000 || echo "  Not in use"

version: ## Show version information
	@echo "$(CYAN)Enterprise CRM$(NC)"
	@grep "VERSION:" .env 2>/dev/null || echo "VERSION: development"
	@echo ""
	@docker-compose version
	@echo ""
	@python3 --version

update: ## Update dependencies
	@echo "$(CYAN)[INFO]$(NC) Updating dependencies..."
	pip install --upgrade -r requirements.txt
	@echo "$(GREEN)[✓]$(NC) Dependencies updated"
