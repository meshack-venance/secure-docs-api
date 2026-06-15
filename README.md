# Secure Document Verification API

A learning-focused Django REST Framework backend for uploading, reviewing, approving, rejecting, and publicly verifying documents.

This project is designed to teach real backend engineering patterns, not just basic CRUD. The goal is to build a small but realistic API like something used by schools, recruitment agencies, government offices, or companies that need to verify whether submitted documents are genuine.

## Problem

Organizations often receive documents such as CVs, certificates, transcripts, licenses, IDs, and contracts through manual channels like email. These documents can be forged, altered, duplicated, hard to track, or difficult to verify later.

## Solution

The API will allow users to upload documents, officers to review them, and public visitors to verify approved documents using a unique verification code.

```text
Document uploaded
-> Pending verification
-> Officer reviews
-> Approved or rejected
-> Public verification link becomes usable
```

Example public verification URL:

```text
https://verify.company.com/doc/ABC123XYZ
```

## Current Status

Phase 1 environment setup has started.

Current files:

```text
requirements.txt
venv/
README.md
```

Installed packages:

```text
Django 5.2.15
Django REST Framework 3.17.1
```

The next step is to design the Django project architecture and folder structure before creating models or endpoints.

## Learning Goals

This project will cover:

- Authentication
- Authorization
- PostgreSQL
- File uploads
- Role-based access control
- Audit logs
- Email notifications
- Search and filtering
- Pagination
- Docker
- Testing
- Deployment
- Production security

## System Users

### Admin

Can manage users, manage officers, view all documents, and view audit logs.

### Verification Officer

Can review documents, approve documents, reject documents, and add review remarks.

### User

Can register, upload documents, view document status, and download their own documents.

### Public Visitor

Can verify document authenticity without logging in.

## Main Features

### Authentication

Planned endpoints:

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
GET  /api/auth/profile
```

### Document Management

Planned endpoints:

```text
POST   /api/documents
GET    /api/documents
GET    /api/documents/{id}
PATCH  /api/documents/{id}
DELETE /api/documents/{id}
```

### Verification Workflow

Document statuses:

```text
PENDING
UNDER_REVIEW
APPROVED
REJECTED
```

Officer action endpoints:

```text
POST /api/documents/{id}/approve
POST /api/documents/{id}/reject
```

### Public Verification

Planned endpoint:

```text
GET /api/verify/{verification_code}
```

Example response:

```json
{
  "verified": true,
  "document_name": "Degree Certificate",
  "status": "APPROVED",
  "issued_date": "2026-06-15"
}
```

### Audit Logging

Actions to track:

```text
Document Uploaded
Status Changed
Officer Approved
Officer Rejected
User Login
Password Reset
```

## Planned Database Design

### User

```text
id
email
first_name
last_name
role
is_active
created_at
```

### Document

```text
id
title
file
description
verification_code
status
uploaded_by
created_at
updated_at
```

### VerificationReview

```text
id
document
officer
decision
remarks
reviewed_at
```

### AuditLog

```text
id
user
action
entity
entity_id
timestamp
```

## Spring Boot to DRF Mental Model

| Spring Boot | Django REST Framework |
| --- | --- |
| Entity | Model |
| Repository | ORM Manager |
| DTO | Serializer |
| Controller | ViewSet or APIView |
| Spring Security | DRF Permissions |
| JWT Filter | SimpleJWT |
| application.properties | settings.py and .env |
| JPA | Django ORM |
| Flyway | Migrations |

## Learning Roadmap

### Phase 1: Environment Setup

- Python
- Virtual environment
- Django
- Django REST Framework
- Git
- PostgreSQL

### Phase 2: Project Architecture

- Django project creation
- App structure
- Custom user model
- Environment variables
- Settings separation

### Phase 3: Authentication System

- JWT
- Registration
- Login
- Refresh tokens
- Profile endpoint
- Permissions

### Phase 4: Document Module

- Models
- Serializers
- ViewSets
- File uploads
- Validation

### Phase 5: Verification Workflow

- Approval process
- Rejection process
- Status transitions
- Business rules

### Phase 6: Public Verification API

- Verification codes
- Public endpoint
- Safe public response shape
- Rate limiting

### Phase 7: Audit Logging

- Audit model
- Signals
- Middleware
- Activity tracking

### Phase 8: Testing

- Unit tests
- API tests
- Permission tests
- Workflow tests

### Phase 9: Docker

- Dockerfile
- Docker Compose
- PostgreSQL container
- Local development environment

### Phase 10: Production Deployment

- Gunicorn
- Nginx
- Render or Railway
- CI/CD
- Production security checks

## Phase 2 Step-by-Step Plan: Project Architecture

Phase 2 is about setting up the shape of the project before building features. A good Django REST Framework project becomes much easier to understand when each app has a clear responsibility.

### Step 1: Confirm the Environment

Make sure the virtual environment is active and Django is available.

```bash
source venv/bin/activate
python --version
django-admin --version
pip show djangorestframework
```

Success means:

```text
Python 3.12.x
Django 5.2.15
djangorestframework installed
```

### Step 2: Create the Django Project

Create the main Django project in the current folder.

```bash
django-admin startproject config .
```

Why `config`?

```text
config/ will hold project-level settings, URLs, ASGI, and WSGI files.
Feature code will live in separate apps.
```

Expected structure:

```text
manage.py
config/
  __init__.py
  asgi.py
  settings.py
  urls.py
  wsgi.py
```

### Step 3: Create the Core Apps

Create separate apps for the main business areas.

```bash
python manage.py startapp accounts
python manage.py startapp documents
python manage.py startapp audits
```

App responsibilities:

```text
accounts/  -> users, roles, authentication, permissions
documents/ -> uploads, document metadata, verification workflow
audits/    -> audit trail and activity history
```

### Step 4: Register Apps in Settings

Add DRF and the local apps to `INSTALLED_APPS` inside `config/settings.py`.

Planned apps:

```text
rest_framework
accounts
documents
audits
```

Success means Django can detect all project apps without errors.

```bash
python manage.py check
```

### Step 5: Decide the Custom User Model Early

Django projects should define a custom user model at the beginning, before the first migration.

Planned user direction:

```text
Use email as the login field.
Add a role field for ADMIN, OFFICER, and USER.
Keep is_active for account control.
```

Why this matters:

```text
Changing the user model later is painful after migrations and data exist.
```

The actual model implementation belongs to Phase 3, but Phase 2 must prepare for it.

### Step 6: Plan Settings Separation

For now, keep `config/settings.py` simple. Later, split settings when the project grows.

Future structure:

```text
config/settings/
  __init__.py
  base.py
  local.py
  production.py
```

Do not split too early unless the project needs it. First learn the normal Django settings file, then refactor with understanding.

### Step 7: Plan Environment Variables

Create an environment strategy before production settings.

Variables this project will eventually need:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DATABASE_URL
EMAIL_HOST
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
```

Recommended future package:

```text
python-decouple
```

This can wait until database and deployment work begin.

### Step 8: Plan URL Structure

Project-level URLs should route into app-level URLs.

Target structure:

```text
config/urls.py
accounts/urls.py
documents/urls.py
audits/urls.py
```

Planned URL prefixes:

```text
/api/auth/
/api/documents/
/api/verify/
/api/audits/
```

### Step 9: Plan Media File Handling

Documents will require file uploads, so the architecture needs media settings.

Planned local settings:

```text
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

Later, production should use external storage instead of keeping uploaded files only on the server disk.

### Step 10: Run the First Architecture Check

After creating the project and apps, run:

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

Success means:

```text
Django starts without errors.
The local server opens.
The app structure is ready for custom user work.
```

### Phase 2 Completion Checklist

- Django project created as `config`
- `manage.py` exists
- `accounts`, `documents`, and `audits` apps exist
- Apps are registered in `INSTALLED_APPS`
- `python manage.py check` passes
- Initial migrations run successfully
- URL strategy is clear
- Media upload strategy is clear
- Custom user model direction is decided before Phase 3

## Local Setup

Activate the virtual environment:

```bash
source venv/bin/activate
```

Check installed versions:

```bash
python --version
django-admin --version
pip show djangorestframework
```

Install dependencies from `requirements.txt` if needed:

```bash
pip install -r requirements.txt
```

## Next Step

Design and create the project architecture:

```text
secure_docs_api/
accounts/
documents/
audits/
config/settings/
```

After that, the first coding milestone will be creating a custom user model with roles.
