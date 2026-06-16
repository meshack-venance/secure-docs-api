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
authentication/
documents/
audits/
```

Installed packages:

```text
Django 5.2.15
Django REST Framework 3.17.1
djangorestframework-simplejwt 5.5.1
drf-spectacular 0.29.0
psycopg 3.3.4
dj-database-url 3.1.2
python-decouple 3.8
```

Phase 4 document management is complete. The project is now being moved from SQLite to PostgreSQL for local development.

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

## Learning Guide for Spring Boot Developers

If you are coming from Spring Boot, read the dedicated DRF guide:

```text
docs/spring-boot-to-drf-guide.md
```

It explains this project from start to end by mapping Spring Boot concepts like Controller, Entity, Repository, DTO, Spring Security, ResponseEntity, ControllerAdvice, Flyway, and Swagger to their Django REST Framework equivalents.

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
GET  /api/accounts/profile/
```

### API Documentation

Swagger/OpenAPI documentation is available through `drf-spectacular`.

```text
GET /api/schema/
GET /api/docs/
```

### Standard API Response Format

All JSON API responses are wrapped in one consistent envelope, similar to the response DTO style commonly used in NestJS or Spring Boot controllers.

Successful response:

```json
{
  "success": true,
  "message": "Document fetched successfully",
  "data": {
    "id": 1,
    "title": "Degree Certificate",
    "status": "PENDING"
  }
}
```

Error response:

```json
{
  "success": false,
  "message": "Authentication credentials were not provided.",
  "data": null,
  "errors": {
    "detail": "Authentication credentials were not provided."
  }
}
```

In this project:

```text
common/renderers.py    -> wraps normal successful API responses
common/exceptions.py   -> wraps validation, permission, auth, and not-found errors
view.response_message  -> sets the success message for a simple view
view.response_messages -> sets success messages per ViewSet action
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
- Completed

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
python manage.py startapp authentication
python manage.py startapp documents
python manage.py startapp audits
```

App responsibilities:

```text
authentication/ -> register, login, refresh-token workflows
accounts/       -> users, roles, profile, permissions
documents/      -> uploads, document metadata, verification workflow
audits/         -> audit trail and activity history
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
authentication/urls.py
accounts/urls.py
documents/urls.py
audits/urls.py
```

Planned URL prefixes:

```text
/api/auth/
/api/accounts/
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

### Step 7: Create Authentication and Account Serializers

Create `authentication/serializers.py` and `accounts/serializers.py`.

Planned serializers:

```text
authentication.RegisterSerializer -> validate registration input and create users
accounts.UserSerializer           -> return safe profile data
```

Do not return password hashes in API responses.

### Step 8: Create Authentication and Account Views

Update `authentication/views.py` and `accounts/views.py`.

Planned views:

```text
authentication.RegisterView
authentication.LoginView
authentication.RefreshTokenView
accounts.ProfileView
```

Login and refresh inherit from SimpleJWT views.

### Step 9: Wire Authentication URLs

Update `authentication/urls.py` and `accounts/urls.py`.

Planned endpoints:

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
GET  /api/accounts/profile/
```

Mapping:

```text
authentication/register/ -> custom RegisterView
authentication/login/    -> SimpleJWT LoginView
authentication/refresh/  -> SimpleJWT RefreshTokenView
accounts/profile/        -> custom ProfileView
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

Update `authentication/tests.py` and `accounts/tests.py`.

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

## Phase 4 Step-by-Step Plan: Document Module

Phase 4 adds the main business object of the system: documents. This phase teaches file uploads, ownership rules, serializers, viewsets, filtering, and API tests.

### Step 1: Confirm Authentication Is Healthy

Run the existing checks before adding document code.

```bash
source venv/bin/activate
python manage.py check
python manage.py test
```

Success means:

```text
The authentication tests pass.
Django reports no system check issues.
```

### Step 2: Design the Document Model

Update `documents/models.py`.

Planned fields:

```text
title
file
description
verification_code
status
uploaded_by
created_at
updated_at
```

Initial statuses:

```text
PENDING
UNDER_REVIEW
APPROVED
REJECTED
```

Important model rules:

```text
uploaded_by links to the custom user model.
verification_code must be unique.
new documents start as PENDING.
file uploads are stored under a documents/ media folder.
```

### Step 3: Generate Verification Codes

Add automatic verification code generation when a document is first created.

Code requirements:

```text
unique
hard to guess
short enough to share
safe for URLs
```

Example:

```text
ABC123XYZ
```

### Step 4: Create and Run Document Migrations

After the model is ready:

```bash
python manage.py makemigrations documents
python manage.py migrate
```

Success means:

```text
documents migration is created.
Document table exists in the database.
No auth model migration errors appear.
```

### Step 5: Register Document in Django Admin

Update `documents/admin.py`.

Admin should show useful fields:

```text
title
status
verification_code
uploaded_by
created_at
updated_at
```

Useful admin filters:

```text
status
created_at
updated_at
```

### Step 6: Create Document Serializers

Create `documents/serializers.py`.

Planned serializers:

```text
DocumentSerializer
DocumentCreateSerializer
```

Serializer rules:

```text
uploaded_by is read-only.
verification_code is read-only.
status is read-only for normal users.
file is required on create.
```

### Step 7: Create Document Permissions

Create `documents/permissions.py`.

Planned permission behavior:

```text
Admins can view all documents.
Officers can view documents for review.
Users can view and manage only their own documents.
Public visitors cannot access document management endpoints.
```

This builds on the `IsAdmin`, `IsOfficer`, and `IsDocumentOwner` concepts from Phase 3.

### Step 8: Create the Document ViewSet

Update `documents/views.py`.

Use a DRF `ModelViewSet` for:

```text
list
create
retrieve
partial_update
destroy
```

Behavior rules:

```text
normal users see only their own documents.
admins and officers can see all documents.
new documents are assigned to request.user.
```

### Step 9: Wire Document URLs

Update `documents/urls.py`.

Use a DRF router.

Target endpoints:

```text
POST   /api/documents/
GET    /api/documents/
GET    /api/documents/{id}/
PATCH  /api/documents/{id}/
DELETE /api/documents/{id}/
```

### Step 10: Validate File Upload Behavior

Test document upload through:

```text
Swagger UI
DRF APIClient
manual multipart request
```

Validation rules to consider:

```text
file is required.
title is required.
only authenticated users can upload.
uploaded files are saved under media/documents/.
```

### Step 11: Add Search, Filtering, and Ordering

Add basic query features.

Planned support:

```text
search by title
filter by status
order by created_at
```

Likely DRF tools:

```text
SearchFilter
OrderingFilter
```

### Step 12: Add Pagination

Configure default pagination for document lists.

Planned behavior:

```text
document lists return paginated results.
page size stays small for development.
```

This prepares the API for real-world document volumes.

### Step 13: Add Document Tests

Update `documents/tests.py`.

Minimum tests:

```text
authenticated user can upload a document.
anonymous user cannot upload a document.
user can list only their own documents.
admin can list all documents.
document receives a verification code.
document starts as PENDING.
user can retrieve own document.
user cannot retrieve another user's document.
```

### Step 14: Verify Swagger Documentation

After the document endpoints are wired, confirm Swagger shows file upload fields.

```bash
python manage.py spectacular --file /tmp/secure-docs-schema.yml
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/api/docs/
```

### Phase 4 Completion Checklist

- `Document` model exists
- verification code generation works
- document migration is created and applied
- document appears in Django admin
- document serializers exist
- ownership permissions exist
- document viewset exists
- document URLs are wired
- authenticated users can upload files
- users can only manage their own documents
- admins and officers can review all documents
- list endpoint supports search, filtering, ordering, and pagination
- document tests pass
- Swagger shows document endpoints

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

## PostgreSQL Setup

The project now reads database settings from environment variables.

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Recommended local `.env` shape:

```env
PORT=4000
DEBUG=True
SECRET_KEY=change-this-local-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=secure_docs_db_local
DATABASE_USER=postgres
DATABASE_PASSWORD=

LOCAL_SERVER=http://localhost:4000
STAGING_SERVER=
PRODUCTION_SERVER=
```

If your `postgres` user has a password, put it in `DATABASE_PASSWORD`.

You can also use a single URL:

```env
DATABASE_URL=postgresql://postgres:mypassword%40123@localhost:5432/secure_docs_db_local
```

If a password contains `@`, write it as `%40` inside `DATABASE_URL`.

Run migrations after PostgreSQL is reachable:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Run the development server on the same style of port you use in other projects:

```bash
python manage.py runserver 0.0.0.0:4000
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
pip show psycopg
pip show dj-database-url
pip show python-decouple
```

Install dependencies from `requirements.txt` if needed:

```bash
pip install -r requirements.txt
```

## Next Step

Finish the local PostgreSQL switch:

```text
Create or update .env
Confirm PostgreSQL is running
Run migrations on secure_docs_db_local
Create a new PostgreSQL-backed superuser
```

After that, the next major milestone will be the verification workflow.
