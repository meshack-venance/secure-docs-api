# Spring Boot to Django REST Framework Guide

This guide teaches Django REST Framework by comparing it with the Spring Boot patterns you already know.

The examples are based on this project: Secure Document Verification API.

## 1. Big Picture

In Spring Boot you usually think like this:

```text
Controller -> Service -> Repository -> Entity -> Database
DTOs       -> Validation -> ResponseEntity
Security   -> Filters / Guards / Method Security
Exceptions -> @ControllerAdvice
```

In Django REST Framework, the common beginner-to-intermediate shape is:

```text
URL -> View -> Serializer -> Model -> Database
Permissions -> Authentication -> Renderer / Exception Handler
```

As the project grows, you can still add a service layer:

```text
URL -> View -> Service -> Serializer / Model -> Database
```

DRF does not force a service layer early. It gives you strong tools for HTTP APIs, validation, permissions, serialization, pagination, filtering, and authentication.

## 2. Concept Mapping

| Spring Boot | Django / DRF | In This Project |
| --- | --- | --- |
| `@SpringBootApplication` | Django project package | `config/` |
| `application.properties` / `.yml` | settings module | `config/settings.py` |
| Controller | View / ViewSet | `authentication/views.py`, `accounts/views.py`, `documents/views.py` |
| `@RequestMapping` / `@GetMapping` | `path()` / router | `authentication/urls.py`, `accounts/urls.py`, `documents/urls.py` |
| Entity | Model | `accounts/models.py`, `documents/models.py` |
| Repository | Django ORM manager/queryset | `Document.objects.filter(...)` |
| DTO | Serializer | `authentication/serializers.py`, `accounts/serializers.py`, `documents/serializers.py` |
| Bean validation | Serializer validation | `serializers.CharField(...)`, `validate_*` |
| Spring Security | Authentication and permissions | SimpleJWT, `CanAccessDocument` |
| `ResponseEntity` | `Response` | `rest_framework.response.Response` |
| `@ControllerAdvice` | Exception handler | `common/exceptions.py` |
| Response wrapper DTO | Renderer / helper response | `common/renderers.py` |
| Flyway / Liquibase | Django migrations | `*/migrations/` |
| springdoc-openapi / Swagger | drf-spectacular | `/api/docs/` |
| JUnit / MockMvc | Django test client / DRF APIClient | `authentication/tests.py`, `accounts/tests.py`, `documents/tests.py` |

## 3. Project Structure

Current structure:

```text
secure-docs-api/
  manage.py
  requirements.txt
  README.md
  config/
    settings.py
    urls.py
    asgi.py
    wsgi.py
  authentication/
    serializers.py
    views.py
    urls.py
    tests.py
  accounts/
    models.py
    serializers.py
    views.py
    urls.py
    permissions.py
    admin.py
    tests.py
    migrations/
  documents/
    models.py
    serializers.py
    views.py
    urls.py
    permissions.py
    admin.py
    tests.py
    migrations/
  audits/
  common/
    renderers.py
    exceptions.py
    responses.py
  docs/
```

Think of `config/` as the main application configuration. Think of `authentication/`, `accounts/`, `documents/`, and `audits/` as domain modules, similar to packages in a Spring Boot project.

## 4. Request Lifecycle

When a client calls:

```text
GET /api/documents/
Authorization: Bearer <access-token>
```

DRF roughly follows this flow:

```text
1. Django receives the HTTP request.
2. config/urls.py routes /api/documents/ to documents.urls.
3. documents/urls.py router maps the request to DocumentViewSet.list().
4. JWT authentication reads the bearer token.
5. Permissions check whether the user can access the endpoint.
6. The view builds a queryset with get_queryset().
7. DRF applies filtering, ordering, and pagination.
8. The serializer converts model objects into JSON-ready data.
9. The custom renderer wraps the result:
   {
     "success": true,
     "message": "...",
     "data": ...
   }
10. Django returns the HTTP response.
```

Spring Boot equivalent:

```text
DispatcherServlet
-> Security filter chain
-> Controller method
-> Service / Repository
-> DTO mapper
-> ResponseEntity
-> JSON response
```

## 5. Settings

File:

```text
config/settings.py
```

This is similar to `application.properties` or `application.yml`.

Important sections:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "rest_framework",
    "drf_spectacular",
    "accounts.apps.AccountsConfig",
    "documents.apps.DocumentsConfig",
    "audits.apps.AuditsConfig",
]
```

This tells Django which apps are active.

Spring Boot comparison:

```text
Component scanning + dependency registration
```

DRF configuration:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "common.renderers.CustomJSONRenderer",
    ),
    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
```

Meaning:

```text
JWTAuthentication       -> read Bearer tokens
IsAuthenticated         -> require login by default
CustomJSONRenderer      -> wrap successful responses
custom_exception_handler -> wrap error responses
AutoSchema              -> generate Swagger/OpenAPI schema
PageNumberPagination    -> paginate list endpoints
```

## 6. URLs

Django has explicit URL routing.

Main router:

```text
config/urls.py
```

Example:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("authentication.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/documents/", include("documents.urls")),
    path("api/audits/", include("audits.urls")),
]
```

Spring Boot comparison:

```java
@RequestMapping("/api/auth")
@RequestMapping("/api/documents")
```

In DRF, app-specific URL files keep each domain clean:

```text
authentication/urls.py
accounts/urls.py
documents/urls.py
```

For viewsets, DRF routers generate REST endpoints automatically:

```python
router = DefaultRouter()
router.register("", DocumentViewSet, basename="document")
router.register("categories", CategoryViewSet, basename="category")
```

This creates endpoints like:

```text
GET    /api/documents/
POST   /api/documents/
GET    /api/documents/{id}/
PUT    /api/documents/{id}/
PATCH  /api/documents/{id}/
DELETE /api/documents/{id}/
```

## 7. Models

Models are like JPA entities.

File:

```text
documents/models.py
```

Example:

```python
class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    document_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    verification_code = models.CharField(max_length=12, unique=True, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
```

Spring Boot equivalent:

```java
@Entity
public class Document {
    @Id
    private Long id;

    private String title;
    private String documentType;

    @ManyToOne
    private User uploadedBy;
}
```

Important Django model field ideas:

```text
CharField      -> varchar
TextField      -> text
EmailField     -> varchar with email validation
BooleanField   -> boolean
DateTimeField  -> timestamp
FileField      -> uploaded file path
ForeignKey     -> many-to-one relationship
TextChoices    -> enum-like choices
```

### Model Methods

This project generates a verification code before saving:

```python
def save(self, *args, **kwargs):
    if not self.verification_code:
        self.verification_code = self._generate_unique_verification_code()

    super().save(*args, **kwargs)
```

Spring Boot comparison:

```text
@PrePersist
```

or service logic before repository save.

## 8. Custom User Model

File:

```text
accounts/models.py
```

This project uses email instead of username:

```python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    USERNAME_FIELD = "email"
```

Spring Boot comparison:

```text
User entity + UserDetails implementation
```

The custom manager creates normal users and superusers:

```python
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        ...

    def create_superuser(self, email, password=None, **extra_fields):
        ...
```

Important rule:

```text
In Django, create the custom user model before your first real migration.
```

Changing the user model later is painful.

## 9. Migrations

Django migrations are like Flyway or Liquibase, but generated from model changes.

Lifecycle:

```text
Change model
-> python manage.py makemigrations
-> migration file is created
-> python manage.py migrate
-> database schema changes
```

Commands:

```bash
venv/bin/python manage.py makemigrations
venv/bin/python manage.py migrate
```

Examples:

Add field:

```python
document_type = models.CharField(max_length=100, blank=True)
```

Then:

```bash
venv/bin/python manage.py makemigrations documents
venv/bin/python manage.py migrate
```

Rename field:

```text
1. Rename the field in the model.
2. Run makemigrations.
3. Django may ask if it is a rename.
4. Confirm if it is truly the same data.
5. Run migrate.
```

If Django does not detect a rename, it may create a remove-field plus add-field migration, which can lose data. In that case, edit carefully or ask before migrating.

## 10. Serializers

Serializers are one of the most important DRF concepts.

They combine three Spring Boot ideas:

```text
DTO
Request validation
Object mapper
```

File:

```text
documents/serializers.py
```

Example:

```python
class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(
        source="uploaded_by.email",
        read_only=True,
    )

    class Meta:
        model = Document
        fields = (
            "id",
            "title",
            "file",
            "document_type",
            "description",
            "verification_code",
            "status",
            "uploaded_by",
            "uploaded_by_email",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "verification_code",
            "status",
            "uploaded_by",
            "uploaded_by_email",
            "created_at",
            "updated_at",
        )
```

What this means:

```text
model            -> use Document model
fields           -> fields exposed by the API
read_only_fields -> client cannot submit or modify these fields
source           -> read data from a related object
```

Spring Boot comparison:

```java
public class DocumentResponseDto {
    private Long id;
    private String title;
    private String uploadedByEmail;
}
```

### Input Serializer vs Output Serializer

This project uses:

```text
DocumentCreateSerializer -> for POST upload
DocumentSerializer       -> for list/detail/update responses
```

Why?

Because create input and output response often have different rules.

Example:

```python
def get_serializer_class(self):
    if self.action == "create":
        return DocumentCreateSerializer

    return DocumentSerializer
```

Spring Boot comparison:

```text
CreateDocumentRequest
DocumentResponse
```

### Serializer create()

In registration:

```python
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)
```

This serializer lives in `authentication/serializers.py` because registration is an authentication workflow.

This is important because passwords must be hashed with `set_password()`, not saved as plain text.

Spring Boot comparison:

```java
passwordEncoder.encode(request.getPassword())
```

## 11. Views

Views are like controllers.

Authentication workflow file:

```text
authentication/views.py
```

Example:

```python
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    response_message = "User registered successfully"
```

This gives you a POST create endpoint.

Spring Boot comparison:

```java
@PostMapping("/register")
public ResponseEntity<UserDto> register(@RequestBody RegisterDto dto) {
    ...
}
```

DRF generic views do a lot automatically:

```text
CreateAPIView   -> POST create
RetrieveAPIView -> GET one object
ListAPIView     -> GET many objects
UpdateAPIView   -> PUT/PATCH
DestroyAPIView  -> DELETE
```

### SimpleJWT Views

Login:

```python
class LoginView(TokenObtainPairView):
    response_message = "User logged in successfully"
```

Refresh:

```python
class RefreshTokenView(TokenRefreshView):
    response_message = "Token refreshed successfully"
```

These inherit token logic from SimpleJWT.

### Profile View

Profile belongs to account data, so it lives in `accounts/views.py`.

```python
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    response_message = "User fetched successfully"

    def get_object(self):
        return self.request.user
```

Normally `RetrieveAPIView` fetches by ID from the URL. Here we override `get_object()` to return the authenticated user.

Spring Boot comparison:

```java
@GetMapping("/profile")
public UserDto profile(Authentication authentication) {
    return userService.getCurrentUser(authentication);
}
```

## 12. ViewSets

ViewSets are controllers that group CRUD actions.

File:

```text
documents/views.py
```

Example:

```python
class DocumentViewSet(viewsets.ModelViewSet):
```

`ModelViewSet` gives:

```text
list           GET /api/documents/
create         POST /api/documents/
retrieve       GET /api/documents/{id}/
update         PUT /api/documents/{id}/
partial_update PATCH /api/documents/{id}/
destroy        DELETE /api/documents/{id}/
```

Spring Boot comparison:

```java
@RestController
@RequestMapping("/api/documents")
public class DocumentController {
    @GetMapping
    @PostMapping
    @GetMapping("/{id}")
    @PutMapping("/{id}")
    @PatchMapping("/{id}")
    @DeleteMapping("/{id}")
}
```

### Querysets

```python
queryset = Document.objects.select_related("uploaded_by")
```

This is the base query.

`select_related("uploaded_by")` avoids extra queries when reading the related user.

Spring Boot comparison:

```text
JOIN FETCH
```

### get_queryset()

```python
def get_queryset(self):
    user = self.request.user
    queryset = self.queryset

    if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
        return queryset.none()

    status = self.request.query_params.get("status")
    if status:
        queryset = queryset.filter(status=status)

    if user.role in (User.Role.ADMIN, User.Role.OFFICER):
        return queryset

    return queryset.filter(uploaded_by=user)
```

This method controls what data the user can see.

Rules:

```text
Anonymous user      -> no documents
Admin / Officer     -> all matching documents
Normal user         -> only own documents
status query param  -> optional filter
```

Spring Boot comparison:

```java
if (user.isAdmin() || user.isOfficer()) {
    return documentRepository.findAll();
}
return documentRepository.findByUploadedBy(user);
```

### perform_create()

```python
def perform_create(self, serializer):
    serializer.save(uploaded_by=self.request.user)
```

This is called during document upload.

The client does not send `uploaded_by`. The backend sets it from the authenticated user.

This prevents a user from pretending to upload a document for someone else.

### destroy()

```python
def destroy(self, request, *args, **kwargs):
    super().destroy(request, *args, **kwargs)
    return Response(None, status=status.HTTP_200_OK)
```

DRF normally returns `204 No Content` for delete. This project returns `200 OK` so the custom response envelope can still be sent.

Response:

```json
{
  "success": true,
  "message": "Document deleted successfully",
  "data": null
}
```

## 13. Permissions

Permissions are like Spring Security authorization rules.

File:

```text
documents/permissions.py
```

Example:

```python
class CanAccessDocument(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role in (User.Role.ADMIN, User.Role.OFFICER):
            return True

        return obj.uploaded_by == request.user
```

Two levels:

```text
has_permission        -> can user access this endpoint at all?
has_object_permission -> can user access this specific object?
```

Spring Boot comparison:

```java
@PreAuthorize("isAuthenticated()")
@PreAuthorize("@securityService.canAccessDocument(authentication, #id)")
```

Global default:

```python
"DEFAULT_PERMISSION_CLASSES": (
    "rest_framework.permissions.IsAuthenticated",
)
```

That means endpoints require authentication unless a view overrides it:

```python
permission_classes = (permissions.AllowAny,)
```

Registration uses `AllowAny` because users must register before they have a token.

## 14. Authentication

This project uses JWT with SimpleJWT.

Endpoints:

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
GET  /api/accounts/profile/
```

Login response:

```json
{
  "success": true,
  "message": "User logged in successfully",
  "data": {
    "refresh": "refresh-token",
    "access": "access-token"
  }
}
```

Authenticated request:

```http
Authorization: Bearer access-token
```

Spring Boot comparison:

```text
JWT filter reads Authorization header
-> validates token
-> sets Authentication in SecurityContext
```

DRF comparison:

```text
JWTAuthentication reads Authorization header
-> validates token
-> sets request.user
```

## 15. Custom Response Envelope

This project returns a consistent response shape:

```json
{
  "success": true,
  "message": "Document fetched successfully",
  "data": {}
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

Files:

```text
common/renderers.py
common/exceptions.py
common/responses.py
```

### Renderer

The renderer wraps successful API responses.

```python
class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        ...
```

It reads:

```python
response_message = "User fetched successfully"
```

or:

```python
response_messages = {
    "list": "Documents fetched successfully",
    "create": "Document uploaded successfully",
}
```

Spring Boot comparison:

```java
return ResponseEntity.ok(
    new ApiResponse<>(true, "User fetched successfully", data)
);
```

The difference is that in this project, the wrapper is global, so controllers/views do not repeat it everywhere.

### Exception Handler

The exception handler wraps errors.

Spring Boot comparison:

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(Exception.class)
    ...
}
```

DRF:

```python
"EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler"
```

### Custom SecureDocsException

NestJS example:

```ts
throw new SecureDocsException(
  "You are not authorized on this resource",
  HttpStatus.UNAUTHORIZED,
  "UNAUTHORIZED",
);
```

DRF equivalent in this project:

```python
from rest_framework import status

from common.exceptions import SecureDocsException


raise SecureDocsException(
    "You are not authorized on this resource",
    status_code=status.HTTP_401_UNAUTHORIZED,
    error="UNAUTHORIZED",
)
```

Response:

```json
{
  "success": false,
  "message": "You are not authorized on this resource",
  "status": 401,
  "error": "UNAUTHORIZED",
  "data": null,
  "errors": {
    "detail": "You are not authorized on this resource"
  }
}
```

Use `SecureDocsException` when you want to stop a request intentionally from your own business logic, similar to throwing a custom `HttpException` in NestJS.

Use DRF's built-in errors for framework-level problems:

```text
serializer validation errors
missing or invalid JWT token
object not found
unsupported HTTP method
```

Use `SecureDocsException` for project rules:

```text
invalid workflow transition
role not allowed to perform a business action
document cannot be verified because it is not approved
invalid custom query parameter
category cannot be deleted because it is still used
```

Current project example:

```python
status_filter = self.request.query_params.get("status")
if status_filter:
    allowed_statuses = {choice.value for choice in Document.Status}
    if status_filter not in allowed_statuses:
        raise SecureDocsException(
            "Invalid document status filter",
            status_code=status.HTTP_400_BAD_REQUEST,
            error="INVALID_DOCUMENT_STATUS",
        )
```

## 16. Filtering, Searching, Ordering, and Pagination

In `DocumentViewSet`:

```python
filter_backends = (filters.SearchFilter, filters.OrderingFilter)
search_fields = ("title", "description", "verification_code")
ordering_fields = ("created_at", "updated_at", "title", "status")
ordering = ("-created_at",)
```

Examples:

```text
GET /api/documents/?search=certificate
GET /api/documents/?ordering=title
GET /api/documents/?ordering=-created_at
GET /api/documents/?status=PENDING
```

Pagination is configured globally:

```python
"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
"PAGE_SIZE": 10,
```

Paginated response data is wrapped:

```json
{
  "success": true,
  "message": "Documents fetched successfully",
  "data": {
    "count": 25,
    "next": "http://localhost:4000/api/documents/?page=2",
    "previous": null,
    "results": []
  }
}
```

Spring Boot comparison:

```text
Pageable
Page<T>
```

## 17. Swagger / OpenAPI

Spring Boot commonly uses Swagger through springdoc-openapi.

This project uses:

```text
drf-spectacular
```

Endpoints:

```text
GET /api/schema/
GET /api/docs/
```

Open Swagger UI:

```text
http://127.0.0.1:4000/api/docs/
```

Generate schema file:

```bash
venv/bin/python manage.py spectacular --file /tmp/secure-docs-schema.yml
```

## 18. Admin Panel

Django includes an admin UI.

Endpoint:

```text
http://127.0.0.1:4000/admin/
```

Create admin user:

```bash
venv/bin/python manage.py createsuperuser
```

Spring Boot comparison:

```text
There is no built-in equivalent in Spring Boot.
You usually build an admin frontend or use external tools.
```

Django admin is useful for development, debugging, and internal operations.

## 19. Database Access

This project is configured for PostgreSQL.

Common `.env` shape:

```env
PORT=4000
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=secure_docs_db_local
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
```

or:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/secure_docs_db_local
```

Run migrations:

```bash
venv/bin/python manage.py migrate
```

Open Django shell:

```bash
venv/bin/python manage.py shell
```

Example ORM queries:

```python
from documents.models import Document

Document.objects.all()
Document.objects.filter(status="PENDING")
Document.objects.get(id=1)
```

Spring Boot comparison:

```java
documentRepository.findAll();
documentRepository.findByStatus(Status.PENDING);
documentRepository.findById(1L);
```

## 20. Testing

Files:

```text
accounts/tests.py
documents/tests.py
```

DRF tests use `APITestCase`.

Example:

```python
response = self.client.post(
    self.login_url,
    {"email": self.email, "password": self.password},
    format="json",
    HTTP_HOST="localhost",
)
```

Spring Boot comparison:

```text
MockMvc
```

Because this project wraps responses at render time, tests use:

```python
body = response.json()
```

instead of only:

```python
response.data
```

Run tests:

```bash
venv/bin/python manage.py test
```

If local PostgreSQL is not ready, you can test logic temporarily with SQLite:

```bash
DATABASE_URL=sqlite:////tmp/secure_docs_api_test.sqlite3 venv/bin/python manage.py test
```

## 21. Development Lifecycle

When adding a new feature, follow this order:

```text
1. Decide the domain object.
2. Add or update the model.
3. Create migrations.
4. Run migrations.
5. Add serializer.
6. Add view or viewset.
7. Add URL route.
8. Add permission rules.
9. Add tests.
10. Check Swagger.
11. Run tests.
```

Example: adding `Category`

```text
documents/models.py       -> Category model
documents/serializers.py  -> CategorySerializer
documents/views.py        -> CategoryViewSet
documents/urls.py         -> router.register("categories", CategoryViewSet)
makemigrations            -> migration file
migrate                   -> database table
tests                     -> API behavior
```

## 22. Common DRF Classes

Useful imports:

```python
from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework import serializers
```

Common views:

```text
APIView          -> most manual
GenericAPIView   -> reusable base with serializer/queryset helpers
CreateAPIView    -> POST create
ListAPIView      -> GET list
RetrieveAPIView  -> GET detail
UpdateAPIView    -> PUT/PATCH
DestroyAPIView   -> DELETE
ModelViewSet     -> full CRUD
```

Common serializer fields:

```text
CharField
EmailField
IntegerField
BooleanField
DateTimeField
FileField
SerializerMethodField
PrimaryKeyRelatedField
```

Common permissions:

```text
AllowAny
IsAuthenticated
IsAdminUser
custom BasePermission
```

## 23. Where to Put Logic

Small projects:

```text
Views can contain simple HTTP orchestration.
Serializers can contain validation and object creation.
Models can contain data rules close to the database.
```

Growing projects:

```text
Move business workflows into services.
Keep views thin.
Keep serializers focused on validation and representation.
Keep models focused on data and invariants.
```

Recommended future structure:

```text
documents/
  services.py
  selectors.py
  permissions.py
  serializers.py
  views.py
```

Possible responsibilities:

```text
services.py  -> commands that change data, like approve_document()
selectors.py -> reusable read queries, like get_documents_for_user()
```

This becomes closer to:

```text
Controller -> Service -> Repository
```

## 24. How to Read This Project

Start here:

```text
config/settings.py
```

Then:

```text
config/urls.py
authentication/urls.py
authentication/views.py
authentication/serializers.py
accounts/urls.py
accounts/views.py
accounts/serializers.py
accounts/models.py
```

Then:

```text
documents/urls.py
documents/views.py
documents/serializers.py
documents/models.py
documents/permissions.py
```

Then:

```text
common/renderers.py
common/exceptions.py
authentication/tests.py
accounts/tests.py
documents/tests.py
```

This reading order follows the real API lifecycle:

```text
Settings -> URL -> View -> Serializer -> Model -> Permission -> Response -> Tests
```

## 25. Commands Cheat Sheet

Activate environment:

```bash
source venv/bin/activate
```

Run server:

```bash
venv/bin/python manage.py runserver 4000
```

Create migrations:

```bash
venv/bin/python manage.py makemigrations
```

Apply migrations:

```bash
venv/bin/python manage.py migrate
```

Create admin:

```bash
venv/bin/python manage.py createsuperuser
```

Run tests:

```bash
venv/bin/python manage.py test
```

Run system check:

```bash
venv/bin/python manage.py check
```

Open shell:

```bash
venv/bin/python manage.py shell
```

Generate OpenAPI schema:

```bash
venv/bin/python manage.py spectacular --file /tmp/secure-docs-schema.yml
```

## 26. Mental Model Summary

If you remember only one mapping, remember this:

```text
Spring Entity        -> Django Model
Spring DTO           -> DRF Serializer
Spring Controller    -> DRF View / ViewSet
Spring Repository    -> Django ORM QuerySet / Manager
Spring Security      -> DRF Authentication + Permission
ControllerAdvice     -> DRF Exception Handler
Response wrapper DTO -> DRF Renderer
Flyway/Liquibase     -> Django Migrations
Swagger              -> drf-spectacular
```

In Spring Boot, you often write more infrastructure yourself. In DRF, many API behaviors are already packaged into generic views, serializers, routers, permissions, and renderers.

The key skill is learning where each responsibility belongs.
