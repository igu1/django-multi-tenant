.PHONY: help migrate runserver superuser create-tenant remove-tenant list-tenants setup-dev test shell collectstatic install requirements clean db-reset db-backup celery-worker celery-beat deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  setup          - Complete project setup"
	@echo "  install        - Install Python dependencies"
	@echo "  requirements   - Update requirements.txt"
	@echo "  migrate        - Run database migrations"
	@echo "  runserver      - Start development server"
	@echo "  shell          - Open Django shell"
	@echo "  superuser      - Create superuser"
	@echo "  create-tenant  - Create new tenant (requires args)"
	@echo "  remove-tenant  - Remove tenant (requires args)"
	@echo "  list-tenants   - List all tenants"
	@echo "  collectstatic  - Collect static files"
	@echo "  test           - Run tests"
	@echo "  test-coverage  - Run tests with coverage"
	@echo "  db-reset       - Reset database (WARNING: deletes all data)"
	@echo "  db-backup      - Backup database"
	@echo "  celery-worker  - Start Celery worker"
	@echo "  celery-beat     - Start Celery beat scheduler"
	@echo "  clean          - Clean temporary files"
	@echo "  deploy         - Deploy to production"

# Setup and Installation
setup:
	@echo "Setting up HRMS project..."
	make install
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	make migrate
	make collectstatic
	@echo "Creating public schema tenant..."
	python3 manage.py create_hrms_tenant --schema_name=public --name="Public" --domain_name=localhost --email=admin@example.com --password=admin123
	@echo "Setup complete! Use 'make runserver' to start."

install:
	pip3 install -r requirements.txt

requirements:
	@echo "Updating requirements.txt..."
	pip3 freeze > requirements.txt
	@echo "Requirements updated!"

# Database operations
makemigrations:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

migrate-tenant:
	@if [ -z "$(schema_name)" ]; then \
		echo "Usage: make migrate-tenant schema_name=tenant_name"; \
		exit 1; \
	fi
	python3 manage.py migrate_schemas --schema=$(schema_name)

migrate-all:
	python3 manage.py migrate_schemas --shared

db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	dropdb hrms_db || true
	createdb hrms_db
	make migrate-all
	make setup

db-backup:
	@echo "Backing up database..."
	pg_dump hrms_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup completed!"

# Development server
runserver:
	python3 manage.py runserver

shell:
	python3 manage.py shell_plus

# Create superuser
superuser:
	python3 manage.py createsuperuser

# Tenant operations
create-tenant:
	@if [ -z "$(schema_name)" ] || [ -z "$(name)" ] || [ -z "$(domain_name)" ] || [ -z "$(email)" ] || [ -z "$(password)" ]; then \
		echo "Usage: make create-tenant schema_name=tenant1 name='Tenant One' domain_name=tenant1.localhost email=admin@tenant1.com password=pass123 [username=admin]"; \
		exit 1; \
	fi
	python3 manage.py create_hrms_tenant --schema_name=$(schema_name) --name="$(name)" --domain_name=$(domain_name) --email=$(email) --password=$(password) --username="$(username)"

remove-tenant:
	@if [ -z "$(schema_name)" ]; then \
		echo "Usage: make remove-tenant schema_name=tenant1"; \
		echo "Add force=1 to skip confirmation"; \
		exit 1; \
	fi
	@if [ "$(force)" = "1" ]; then \
		python3 manage.py remove_tenant --schema_name=$(schema_name) --force; \
	else \
		python3 manage.py remove_tenant --schema_name=$(schema_name); \
	fi

list-tenants:
	python3 manage.py list_tenants

# Static files
collectstatic:
	python3 manage.py collectstatic --noinput


# Celery
celery-worker:
	celery -A core worker --loglevel=info

celery-beat:
	celery -A core beat --loglevel=info

# Maintenance
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/
	rm -rf staticfiles/
	@echo "Clean completed!"

# Production deployment
deploy:
	@echo "Deploying to production..."
	make install
	make collectstatic
	make migrate
	@echo "Deployment completed!"

# Development setup (legacy)
setup-dev:
	make setup

# Quick start commands
quick-start:
	@echo "Quick start for HRMS:"
	@echo "1. make setup"
	@echo "2. make runserver"
	@echo "3. Visit http://localhost:8000"

# Database info
db-info:
	@echo "Database Information:"
	@echo "Name: hrms_db"
	@echo "Host: localhost"
	@echo "Port: 5432"
	@echo "User: postgres"
