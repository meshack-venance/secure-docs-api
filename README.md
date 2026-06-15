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

Phase 3 authentication is complete.

Current files:

```text
requirements.txt
README.md
manage.py
config/
accounts/
documents/
audits/
```

Installed packages:

```text
Django 5.2.15
Django REST Framework 3.17.1
djangorestframework-simplejwt 5.5.1
drf-spectacular 0.29.0
```

The next major step is Phase 4: building the document upload module.

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

Implemented endpoints:

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
GET  /api/auth/profile/
```

### API Documentation

Swagger/OpenAPI documentation is available through `drf-spectacular`.

```text
GET /api/schema/
GET /api/docs/
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
| Swagger / springdoc-openapi | drf-spectacular |
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
- Completed

### Phase 3: Authentication System

- JWT
- Registration
- Login
- Refresh tokens
- Profile endpoint
- Permissions
- Completed

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
python manage.py runserver
```

Success means:

```text
Django starts without errors.
The local server opens.
The app structure is ready for custom user work.
```

Do not run the first database migration until the custom user model is created in Phase 3.

### Phase 2 Completion Checklist

- Django project created as `config`
- `manage.py` exists
- `accounts`, `documents`, and `audits` apps exist
- Apps are registered in `INSTALLED_APPS`
- `python manage.py check` passes
- Initial migrations were deferred until the custom user model existed
- URL strategy is clear
- Media upload strategy is clear
- Custom user model direction is decided before Phase 3

## Phase 3 Step-by-Step Plan: Authentication System

Phase 3 turns the project into a real API with users, roles, and token-based authentication. The most important rule is to create the custom user model before running the first migration.

### Step 1: Confirm Phase 2 Is Clean

Run the Django system check before editing authentication code.

```bash
source venv/bin/activate
python manage.py check
```

Success means:

```text
System check identified no issues
```

### Step 2: Install JWT Support

Add SimpleJWT for access and refresh tokens.

```bash
pip install djangorestframework-simplejwt
pip freeze > requirements.txt
```

Why:

```text
DRF handles API structure.
SimpleJWT handles token creation, refresh, and authentication.
```

### Step 3: Create the Custom User Model

Update `accounts/models.py` with a custom user model.

Planned fields:

```text
email
first_name
last_name
role
is_active
is_staff
date_joined
```

Planned roles:

```text
ADMIN
OFFICER
USER
```

Design decision:

```text
email will be the login field.
username will not be used.
```

### Step 4: Create the User Manager

Create a custom manager for user creation.

Required methods:

```text
create_user(email, password, **extra_fields)
create_superuser(email, password, **extra_fields)
```

Why:

```text
Django needs a manager that knows how to create normal users and admin users when email replaces username.
```

### Step 5: Register the Custom User in Settings

Add this to `config/settings.py`:

```python
AUTH_USER_MODEL = "accounts.User"
```

This must happen before the first migration.

### Step 6: Configure DRF Authentication

Add REST framework authentication settings in `config/settings.py`.

Planned configuration:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}
```

Why:

```text
Most API endpoints should require login by default.
Public endpoints will explicitly allow anonymous access later.
```

### Step 7: Create Authentication Serializers

Create `accounts/serializers.py`.

Planned serializers:

```text
RegisterSerializer
UserSerializer
```

Serializer responsibilities:

```text
RegisterSerializer -> validate input and create users
UserSerializer     -> return safe profile data
```

Do not return password hashes in API responses.

### Step 8: Create Authentication Views

Update `accounts/views.py`.

Planned views:

```text
RegisterView
ProfileView
```

SimpleJWT will provide login and refresh views.

### Step 9: Wire Authentication URLs

Update `accounts/urls.py`.

Planned endpoints:

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
GET  /api/auth/profile/
```

Mapping:

```text
register/ -> custom RegisterView
login/    -> SimpleJWT TokenObtainPairView
refresh/  -> SimpleJWT TokenRefreshView
profile/  -> custom ProfileView
```

### Step 10: Create Role-Based Permissions

Create `accounts/permissions.py`.

Planned permissions:

```text
IsAdmin
IsOfficer
IsDocumentOwner
```

These permissions will be used heavily in later phases when documents and verification workflows are built.

### Step 11: Make and Run the First Migrations

Only run migrations after the custom user model and `AUTH_USER_MODEL` are in place.

```bash
python manage.py makemigrations
python manage.py migrate
```

Success means:

```text
accounts migration is created.
Database tables are created.
No custom user model errors appear.
```

### Step 12: Create a Superuser

Create the first admin user.

```bash
python manage.py createsuperuser
```

Expected login field:

```text
Email
```

If Django asks for `Username`, the custom user setup is not correct yet.

### Step 13: Test the Authentication Flow Manually

Run the server.

```bash
python manage.py runserver
```

Manual checks:

```text
Register a user.
Log in and receive access plus refresh tokens.
Use the access token to call profile.
Refresh the token successfully.
```

### Step 14: Add Authentication Tests

Update `accounts/tests.py`.

Minimum tests:

```text
User can register.
User can log in.
Authenticated user can view profile.
Anonymous user cannot view profile.
Superuser is created with ADMIN role.
```

### Phase 3 Completion Checklist

- SimpleJWT installed and saved in `requirements.txt`
- Custom email-based user model exists
- Custom user manager exists
- `AUTH_USER_MODEL` is configured
- DRF uses JWT authentication
- Register endpoint works
- Login endpoint returns tokens
- Refresh endpoint returns a new access token
- Profile endpoint requires authentication
- Role permission classes are started
- First migrations are created and applied
- Superuser creation uses email
- Authentication tests pass

## API Documentation

Run the development server:

```bash
python manage.py runserver
```

Open Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

Open the raw OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

Generate the schema from the command line:

```bash
python manage.py spectacular --file /tmp/secure-docs-schema.yml
```

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
pip show djangorestframework-simplejwt
pip show drf-spectacular
```

Install dependencies from `requirements.txt` if needed:

```bash
pip install -r requirements.txt
```

## Next Step

Implement Phase 4 document management:

```text
Document model
Document serializer
File uploads
Document owner permissions
Document CRUD endpoints
```

After that, the next major milestone will be the verification workflow.
