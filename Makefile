# Use the checked-in virtual environment path so every command runs with project deps.
PYTHON := venv/bin/python
MANAGE := $(PYTHON) manage.py

# CI-style commands use temporary SQLite databases so they do not depend on local Postgres.
TEST_DATABASE_URL := sqlite:////tmp/secure_docs_api_test.sqlite3
SCHEMA_DATABASE_URL := sqlite:////tmp/secure_docs_api_schema.sqlite3
MIGRATION_CHECK_DATABASE_URL := sqlite:////tmp/secure_docs_api_migration_check.sqlite3
SCHEMA_FILE := /tmp/secure-docs-schema.yml

# Override these at the command line, for example: make run PORT=8000.
PORT ?= 4000
APP ?=

.PHONY: help run check test test-app migrate makemigrations migration-check schema shell createsuperuser verify

# Default discovery command for humans.
help:
	@echo "Secure Docs API commands"
	@echo ""
	@echo "Usage:"
	@echo "  make run                         Start development server on PORT=$(PORT)"
	@echo "  make check                       Run Django system checks"
	@echo "  make test                        Run full test suite with SQLite test DB"
	@echo "  make test-app APP=authentication Run tests for one app"
	@echo "  make makemigrations              Create Django migrations"
	@echo "  make migrate                     Apply Django migrations"
	@echo "  make migration-check             Check for missing migrations"
	@echo "  make schema                      Generate OpenAPI schema"
	@echo "  make shell                       Open Django shell"
	@echo "  make createsuperuser             Create Django superuser"
	@echo "  make verify                      Run checks used before commits"

# Local development server.
run:
	$(MANAGE) runserver 0.0.0.0:$(PORT)

# Fast Django project validation without running tests.
check:
	$(MANAGE) check

# Full test suite against an isolated SQLite database.
test:
	DATABASE_URL=$(TEST_DATABASE_URL) $(MANAGE) test

# Focus one app while learning or debugging: make test-app APP=documents.
test-app:
	@if [ -z "$(APP)" ]; then \
		echo "Usage: make test-app APP=authentication"; \
		exit 1; \
	fi
	DATABASE_URL=$(TEST_DATABASE_URL) $(MANAGE) test $(APP)

# Migration commands intentionally use the configured development database.
makemigrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

# Fails when model changes exist without matching migration files.
migration-check:
	DATABASE_URL=$(MIGRATION_CHECK_DATABASE_URL) $(MANAGE) makemigrations --check --dry-run

# Generate the OpenAPI schema used by Swagger UI and contract checks.
schema:
	DATABASE_URL=$(SCHEMA_DATABASE_URL) $(MANAGE) spectacular --file $(SCHEMA_FILE)

# Handy interactive Django commands.
shell:
	$(MANAGE) shell

createsuperuser:
	$(MANAGE) createsuperuser

# One command to run before commits or pushes.
verify: check test schema migration-check
