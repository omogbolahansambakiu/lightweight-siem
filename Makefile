.PHONY: help up down restart logs clean test lint setup-indices load-rules dev

# Default target
help:
	@echo "Lightweight SIEM - Available Commands:"
	@echo ""
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - View logs from all services"
	@echo "  make logs-f          - Follow logs from all services"
	@echo "  make clean           - Clean all data (WARNING: destructive)"
	@echo "  make setup           - Initial setup (indices, rules, etc.)"
	@echo "  make setup-indices   - Create OpenSearch indices"
	@echo "  make load-rules      - Load detection rules"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make lint            - Run linters"
	@echo "  make format          - Format code"
	@echo "  make dev             - Start in development mode"
	@echo "  make build           - Build Docker images"
	@echo "  make health          - Check service health"
	@echo "  make backup          - Backup OpenSearch data"
	@echo "  make restore         - Restore OpenSearch data"
	@echo ""

# Start services
up:
	docker compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@make health

# Stop services
down:
	docker compose down

# Restart services
restart:
	docker compose restart

# View logs
logs:
	docker compose logs

logs-f:
	docker compose logs -f

# Clean all data
clean:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		rm -rf data/opensearch/*; \
		rm -rf data/redis/*; \
		rm -rf data/logs/**/*; \
		echo "Data cleaned"; \
	fi

# Build images
build:
	docker-compose build

# Initial setup
setup: setup-indices load-rules
	@echo "Initial setup complete!"

# Setup OpenSearch indices
setup-indices:
	@echo "Creating OpenSearch indices..."
	bash scripts/setup/create_indices.sh

# Load detection rules
load-rules:
	@echo "Loading detection rules..."
	docker-compose exec -T detection-engine python -m engine.rule_loader

# Run tests
test: test-unit test-integration

test-unit:
	@echo "Running unit tests..."
	docker-compose exec -T detection-engine pytest tests/unit -v
	docker-compose exec -T alert-manager pytest tests/unit -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration -v

# Code quality
lint:
	@echo "Running linters..."
	docker-compose exec -T detection-engine flake8 .
	docker-compose exec -T alert-manager flake8 .
	docker-compose exec -T api flake8 .

format:
	@echo "Formatting code..."
	docker-compose exec -T detection-engine black .
	docker-compose exec -T alert-manager black .
	docker-compose exec -T api black .

# Development mode
dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Health check
health:
	@echo "Checking service health..."
	@echo -n "OpenSearch: "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:9200 && echo " ✓" || echo " ✗"
	@echo -n "Redis: "
	@docker-compose exec -T redis redis-cli ping | grep -q PONG && echo " ✓" || echo " ✗"
	@echo -n "API: "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health && echo " ✓" || echo " ✗"
	@echo -n "Frontend: "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 && echo " ✓" || echo " ✗"

# Backup
backup:
	@echo "Creating backup..."
	bash scripts/maintenance/backup.sh

# Restore
restore:
	@echo "Restoring from backup..."
	bash scripts/maintenance/restore.sh

# Scale services
scale-detection:
	docker-compose up -d --scale detection-engine=4

# Generate test logs
generate-test-logs:
	python scripts/testing/generate_test_logs.py

# View metrics
metrics:
	@echo "Opening Prometheus metrics..."
	@open http://localhost:9090 || xdg-open http://localhost:9090

# View dashboards
dashboard:
	@echo "Opening Grafana dashboard..."
	@open http://localhost:3001 || xdg-open http://localhost:3001

# Install dependencies
install-deps:
	pip install -r detection-engine/requirements.txt
	pip install -r alert-manager/requirements.txt
	pip install -r api/requirements.txt
	cd frontend && npm install
