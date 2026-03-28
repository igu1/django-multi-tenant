# HRMS - Multi-Tenant Human Resource Management System

A Django-based Multi-Tenant Human Resource Management System built with modern best practices using django-tenants for semi-isolated multi-tenancy.

## Features

- **Multi-Tenant Architecture**: Each tenant gets their own isolated PostgreSQL schema
- **Employee Management**: Manage employees across different organizations
- **Task Management**: Task creation and assignment per tenant
- **Leave Management**: Leave request management with tenant-specific policies
- **Dashboard Analytics**: Analytics and reporting per tenant
- **REST API**: Full REST API support with Django REST Framework
- **Background Tasks**: Celery for background task processing
- **PostgreSQL Schemas**: Semi-isolated approach using PostgreSQL schemas

## Multi-Tenant Architecture

This project uses a **semi-isolated approach** with PostgreSQL schemas:

- Each tenant gets their own schema in the database
- Data is completely isolated between tenants
- Shared apps (like authentication) use the public schema
- Tenant-specific apps use individual schemas
- Domain-based tenant identification (e.g., `tenant1.localhost`)

## Model Rules (Important)

### 1) Tenant-scoped models

If a model is meant to live inside a tenant schema (tenant data), it **must** inherit from `TenantScopedModel`.

Source of truth: `apps/tenants/models.py`

What `TenantScopedModel` gives you:

- `tenant` FK (required)
- `objects` manager that auto-filters by the current tenant
- `all_objects` manager that bypasses tenant filtering

Example:

```python
from apps.tenants.models import TenantScopedModel

class Employee(TenantScopedModel):
    full_name = models.CharField(max_length=255)
```

### 2) Non-tenant (shared) models

If a model is shared across all tenants (public schema data), it **must not** inherit from `TenantScopedModel`.

Example use-cases:

- Tenants & Domains models
- Shared configuration
- Shared identities (if you decide to keep some data global)

## How tenant scoping works (Flow)

### Request → schema selection

For each request:

- `TenantMainMiddleware` resolves the tenant from the hostname (example: `ez.localhost`).
- Django-tenants sets `connection.tenant` and switches the DB schema.

### ORM filtering (why you must inherit)

`TenantScopedModel.objects` uses a tenant-aware manager:

- If `connection.tenant` is missing or is `public`, it returns the unfiltered queryset.
- If a real tenant is active, it auto-adds `WHERE tenant_id = <current tenant>`.

So the rule is simple:

- **Tenant data models**: inherit `TenantScopedModel`
- **Shared data models**: do not inherit

## Project Structure

```
HRMS/
├── core/                   # Django project settings
│   ├── __init__.py        # Celery app initialization
│   ├── celery.py          # Celery configuration
│   ├── settings.py        # Django settings with multi-tenant config
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── apps/                  # Django applications directory
│   ├── tenants/          # Multi-tenant management app
│   │   ├── management/   # Custom management commands
│   │   ├── models.py     # User, Tenant, Domain models
│   │   ├── admin.py      # Admin configuration
│   │   └── urls.py       # Tenant URL patterns
│   ├── tasks/            # Task management app (tenant-specific)
│   ├── leave/            # Leave management app (tenant-specific)
│   └── dashboard/        # Dashboard app (tenant-specific)
├── static/               # Static files (CSS, JS, images)
├── media/               # User uploaded files
├── templates/           # HTML templates
├── requirements.txt      # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore file
└── manage.py           # Django management script
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (for Celery)

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd HRMS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb hrms_db

# Copy environment file
cp .env.example .env
# Edit .env file with your database configuration
```

### 3. Database Migrations

```bash
# Migrate public schema (shared apps)
make migrate-all

# Create a tenant
make create-tenant schema_name=tenant1 name="First Organization" domain_name=tenant1.localhost email=admin@tenant1.com password=admin123

# Migrate tenant schemas
make migrate
```

### 4. Create Superuser and Run Server

```bash
# Create superuser for public schema
make superuser

# Start development server
make runserver
```

## Tenant Management

### Creating New Tenants

Use the management command to create new tenants:

```bash
make create-tenant schema_name=company_name name="Company Name" domain_name=company_name.localhost email=admin@company_name.com password=secure_password
```

### Accessing Tenants

Access tenant-specific data using subdomains:
- Public: `http://localhost:8000`
- Tenant 1: `http://tenant1.localhost:8000`
- Tenant 2: `http://tenant2.localhost:8000`

### Managing Tenants via Admin

Access the Django admin at `http://localhost:8000/admin` to:
- Manage tenants and domains
- Create tenant-specific users
- Configure tenant settings

## User + Tenant behavior

- Superusers can be treated as shared by keeping `User.tenant = None`.
- Normal users should have `User.tenant` set.
- Admin enforces tenant assignment rules and supports editing `tenant` for superusers.

## Shared vs Tenant Apps

### Shared Apps (Public Schema)
- `apps.tenants` - User and tenant management
- Django auth and admin
- REST Framework
- Celery configuration

### Tenant Apps (Per-Schema)
- `apps.tasks` - Task management
- `apps.leave` - Leave management  
- `apps.dashboard` - Analytics and reporting

## Technology Stack

- **Backend**: Django 5.1.15 with django-tenants 3.7.0
- **Database**: PostgreSQL with schema-based multi-tenancy
- **API**: Django REST Framework 3.15.2
- **Task Queue**: Celery 5.6.3 with Redis
- **Static Files**: WhiteNoise 6.12.0
- **Environment**: python-decouple 3.8

## Development

### Running Migrations

```bash
# Create migrations
make makemigrations

# Migrate shared apps (public schema)
make migrate-all

# Migrate all tenant schemas
make migrate

# Migrate specific tenant
make migrate-tenant schema_name=tenant_name
```

### Creating Superusers

```bash
# For public schema
make superuser
```

### Tenant Management

```bash
# Create a new tenant
make create-tenant schema_name=company_name name="Company Name" domain_name=company_name.localhost email=admin@company_name.com password=secure_password

# List all tenants
make list-tenants

# Remove a tenant
make remove-tenant schema_name=company_name

# Remove tenant without confirmation
make remove-tenant schema_name=company_name force=1
```

### Development Server

```bash
# Start development server
make runserver

# Open Django shell
make shell
```

### Testing

```bash
# Run tests for all apps
make test

# Run tests for specific app
python manage.py test apps.tasks
```

### Maintenance

```bash
# Clean temporary files
make clean

# Collect static files
make collectstatic

# Backup database
make db-backup

# Reset database (WARNING: deletes all data)
make db-reset
```

## Deployment Considerations

### Database
- PostgreSQL is required for schema-based multi-tenancy
- Ensure proper permissions for schema creation
- Consider connection pooling for multiple tenants

### Domain Configuration
- Configure wildcard subdomains in DNS
- Update ALLOWED_HOSTS to support tenant domains
- Set up SSL certificates for tenant domains

### Performance
- Monitor schema-specific performance
- Consider connection pooling per tenant
- Implement caching strategies per tenant

## Security

- Each tenant has complete data isolation
- Schema-based separation prevents data leaks
- Tenant-specific user authentication
- Admin access controlled per tenant

## API Usage

Each tenant gets their own API endpoints:

```
# Tenant-specific API
http://tenant1.localhost:8000/api/tasks/
http://tenant1.localhost:8000/api/leave/
http://tenant1.localhost:8000/api/dashboard/

# Public API (shared)
http://localhost:8000/api/public/
```

### Tasks API

#### Endpoints
- `GET/POST /api/tasks/` - List and create tasks
- `GET/PUT/PATCH/DELETE /api/tasks/{id}/` - Retrieve, update, delete tasks
- `GET/POST /api/statuses/` - Manage task statuses (per tenant)
- `GET/PUT/PATCH/DELETE /api/statuses/{id}/` - CRUD task statuses
- `GET/POST /api/priorities/` - Manage task priorities (per tenant)
- `GET/PUT/PATCH/DELETE /api/priorities/{id}/` - CRUD task priorities

#### Filtering
Use query parameters to filter tasks:
```
?status=1                    # Filter by status ID
?priority=2                  # Filter by priority ID
?assigned_to=3               # Filter by assigned user ID
?created_by=1                # Filter by creator user ID
?status=1&priority=2         # Multiple filters
```

#### Search & Ordering
```
?search=urgent               # Search in title and description
?ordering=-created_at        # Order by creation date (newest first)
?ordering=due_date           # Order by due date
?search=report&ordering=-priority  # Combine search and ordering
```

#### Tenant Behavior
- **Non-superusers**: Only see tasks in their tenant
- **Superusers**: Can see tasks across all tenants
- **Dropdowns**: Statuses, priorities, and users are filtered to current tenant
- **Auto-assignment**: `tenant` and `created_by` set automatically on create

## License

This project is licensed under the MIT License.
