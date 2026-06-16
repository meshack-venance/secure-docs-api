from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from accounts.models import User
from common.exceptions import SecureDocsException
from documents.models import Category, Document
from documents.permissions import CanAccessDocument
from documents.serializers import (
    CategorySerializer,
    DocumentCreateSerializer,
    DocumentReviewSerializer,
    DocumentSerializer,
)


DOCUMENT_EXAMPLE = {
    "id": 1,
    "title": "Degree Certificate",
    "file": "http://localhost:4000/media/documents/degree-certificate.pdf",
    "document_type": "Certificate",
    "description": "Bachelor degree certificate for Meshack Venance",
    "verification_code": "AB12CD34E",
    "status": "PENDING",
    "uploaded_by": 1,
    "uploaded_by_email": "meshackvenance99@gmail.com",
    "reviewed_by": None,
    "reviewed_by_email": None,
    "reviewed_at": None,
    "review_notes": "",
    "created_at": "2026-06-16T10:00:00Z",
    "updated_at": "2026-06-16T10:00:00Z",
}

DOCUMENT_UPLOAD_EXAMPLE = {
    "title": "Degree Certificate",
    "file": "<binary file>",
    "description": "Bachelor degree certificate for Meshack Venance",
}

DOCUMENT_LIST_EXAMPLE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [DOCUMENT_EXAMPLE],
}

REVIEW_REQUEST_EXAMPLE = {
    "action": "APPROVE",
    "review_notes": "Document details match official records.",
}

REJECTION_REQUEST_EXAMPLE = {
    "action": "REJECT",
    "review_notes": "Certificate number could not be verified.",
}

START_REVIEW_REQUEST_EXAMPLE = {
    "action": "START_REVIEW",
    "review_notes": "Initial review started.",
}

CATEGORY_EXAMPLE = {
    "id": 1,
    "name": "Certificates",
    "description": "Academic and professional certificates",
    "created_at": "2026-06-16T10:00:00Z",
}

CATEGORY_LIST_EXAMPLE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [CATEGORY_EXAMPLE],
}

INVALID_STATUS_EXAMPLE = {
    "success": False,
    "message": "Invalid document status filter",
    "status": 400,
    "error": "INVALID_DOCUMENT_STATUS",
    "data": None,
}


@extend_schema_view(
    list=extend_schema(
        summary="List documents",
        description="Return documents visible to the authenticated user. Admins and officers can see all documents.",
        parameters=[
            OpenApiParameter(
                name="status",
                description="Filter documents by status.",
                required=False,
                type=str,
                enum=[choice.value for choice in Document.Status],
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Documents fetched successfully",
                examples=[
                    OpenApiExample(
                        "Documents fetched response",
                        value={
                            "success": True,
                            "message": "Documents fetched successfully",
                            "data": DOCUMENT_LIST_EXAMPLE,
                        },
                    ),
                ],
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Invalid document status filter",
                examples=[
                    OpenApiExample(
                        "Invalid status response",
                        value=INVALID_STATUS_EXAMPLE,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Documents fetched response",
                value={
                    "success": True,
                    "message": "Documents fetched successfully",
                    "data": DOCUMENT_LIST_EXAMPLE,
                },
                response_only=True,
            ),
            OpenApiExample(
                "Invalid status response",
                value=INVALID_STATUS_EXAMPLE,
                response_only=True,
                status_codes=["400"],
            ),
        ],
    ),
    create=extend_schema(
        summary="Upload document",
        description="Upload a document file for verification.",
        request={"multipart/form-data": DocumentCreateSerializer},
        examples=[
            OpenApiExample(
                "Document upload request",
                value=DOCUMENT_UPLOAD_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Document uploaded response",
                value={
                    "success": True,
                    "message": "Document uploaded successfully",
                    "data": DOCUMENT_EXAMPLE,
                },
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get document",
        description="Return one document if the authenticated user can access it.",
        examples=[
            OpenApiExample(
                "Document fetched response",
                value={
                    "success": True,
                    "message": "Document fetched successfully",
                    "data": DOCUMENT_EXAMPLE,
                },
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Partially update document",
        description="Update one or more editable document fields.",
        request={"multipart/form-data": DocumentCreateSerializer},
        examples=[
            OpenApiExample(
                "Document patch request",
                value={
                    "description": "Updated certificate description",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Document patched response",
                value={
                    "success": True,
                    "message": "Document updated successfully",
                    "data": {
                        **DOCUMENT_EXAMPLE,
                        "description": "Updated certificate description",
                    },
                },
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Delete document",
        description="Delete one document if the authenticated user can access it.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Document deleted successfully",
                examples=[
                    OpenApiExample(
                        "Document deleted response",
                        value={
                            "success": True,
                            "message": "Document deleted successfully",
                            "data": None,
                        },
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Document deleted response",
                value={
                    "success": True,
                    "message": "Document deleted successfully",
                    "data": None,
                },
                response_only=True,
            ),
        ],
    ),
)
class DocumentViewSet(viewsets.ModelViewSet):
    """Document CRUD with ownership filtering and project response messages."""

    queryset = Document.objects.select_related("uploaded_by", "reviewed_by")
    permission_classes = (CanAccessDocument,)
    # JSON keeps command endpoints ergonomic; multipart/form-data enables file uploads.
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    # Document edits are partial-only in this API, so PUT/full replacement is disabled.
    http_method_names = ("get", "post", "patch", "delete", "head", "options")
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("title", "description", "verification_code")
    ordering_fields = ("created_at", "updated_at", "title", "status")
    ordering = ("-created_at",)
    response_messages = {
        "list": "Documents fetched successfully",
        "create": "Document uploaded successfully",
        "retrieve": "Document fetched successfully",
        "partial_update": "Document updated successfully",
        "destroy": "Document deleted successfully",
    }

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        # Schema generation has no real user, so keep docs generation side-effect free.
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return queryset.none()

        status_filter = self.request.query_params.get("status")
        if status_filter:
            allowed_statuses = {choice.value for choice in Document.Status}
            if status_filter not in allowed_statuses:
                raise SecureDocsException(
                    "Invalid document status filter",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error="INVALID_DOCUMENT_STATUS",
                )

            queryset = queryset.filter(status=status_filter)

        if user.role in (User.Role.ADMIN, User.Role.OFFICER):
            return queryset

        # Normal users should never see documents uploaded by another account.
        return queryset.filter(uploaded_by=user)

    def get_serializer_class(self):
        # DRF calls this per action, similar to choosing different DTOs per controller method.
        if self.action == "create":
            return DocumentCreateSerializer
        if self.action == "review":
            return DocumentReviewSerializer

        return DocumentSerializer

    def perform_create(self, serializer):
        # Ownership comes from the JWT user, never from client-submitted data.
        serializer.save(uploaded_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Return 200 so the global renderer can still emit the standard envelope.
        super().destroy(request, *args, **kwargs)
        return Response(None, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Review document",
        description=(
            "Run a document review action. Only admins and officers can start review, "
            "approve, or reject documents."
        ),
        request=DocumentReviewSerializer,
        examples=[
            OpenApiExample(
                "Start review request",
                value=START_REVIEW_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Approve request",
                value=REVIEW_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Reject request",
                value=REJECTION_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Review started response",
                value={
                    "success": True,
                    "message": "Document review started successfully",
                    "data": {
                        **DOCUMENT_EXAMPLE,
                        "status": "UNDER_REVIEW",
                        "reviewed_by": 2,
                        "reviewed_by_email": "officer@example.com",
                        "reviewed_at": "2026-06-16T10:15:00Z",
                        "review_notes": "Initial review started.",
                    },
                },
                response_only=True,
            ),
            OpenApiExample(
                "Approved response",
                value={
                    "success": True,
                    "message": "Document approved successfully",
                    "data": {
                        **DOCUMENT_EXAMPLE,
                        "status": "APPROVED",
                        "reviewed_by": 2,
                        "reviewed_by_email": "officer@example.com",
                        "reviewed_at": "2026-06-16T10:30:00Z",
                        "review_notes": "Document details match official records.",
                    },
                },
                response_only=True,
            ),
            OpenApiExample(
                "Rejected response",
                value={
                    "success": True,
                    "message": "Document rejected successfully",
                    "data": {
                        **DOCUMENT_EXAMPLE,
                        "status": "REJECTED",
                        "reviewed_by": 2,
                        "reviewed_by_email": "officer@example.com",
                        "reviewed_at": "2026-06-16T10:45:00Z",
                        "review_notes": "Certificate number could not be verified.",
                    },
                },
                response_only=True,
            ),
        ],
    )
    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        document = self.get_object()
        self._ensure_can_review(request.user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action_name = serializer.validated_data["action"]
        # Validate the transition before mutating the document.
        next_status = self._get_review_status(document, action_name)
        self.response_message = self._get_review_message(action_name)

        self._apply_review_state(
            document,
            request.user,
            next_status,
            serializer.validated_data.get("review_notes", ""),
        )

        return Response(DocumentSerializer(document, context={"request": request}).data)

    def _get_review_status(self, document, action_name):
        # Keep status-transition rules in one place so every review action is consistent.
        if action_name == DocumentReviewSerializer.START_REVIEW:
            self._ensure_pending(document)
            return Document.Status.UNDER_REVIEW

        if action_name == DocumentReviewSerializer.APPROVE:
            self._ensure_decidable(document)
            return Document.Status.APPROVED

        if action_name == DocumentReviewSerializer.REJECT:
            self._ensure_decidable(document)
            return Document.Status.REJECTED

        raise SecureDocsException(
            "Invalid document review action",
            status_code=status.HTTP_400_BAD_REQUEST,
            error="INVALID_DOCUMENT_REVIEW_ACTION",
        )

    def _get_review_message(self, action_name):
        messages = {
            DocumentReviewSerializer.START_REVIEW: "Document review started successfully",
            DocumentReviewSerializer.APPROVE: "Document approved successfully",
            DocumentReviewSerializer.REJECT: "Document rejected successfully",
        }
        return messages[action_name]

    def _ensure_can_review(self, user):
        if user.role not in (User.Role.ADMIN, User.Role.OFFICER):
            raise SecureDocsException(
                "Only admins and officers can review documents",
                status_code=status.HTTP_403_FORBIDDEN,
                error="DOCUMENT_REVIEW_FORBIDDEN",
            )

    def _ensure_pending(self, document):
        if document.status != Document.Status.PENDING:
            raise SecureDocsException(
                "Only pending documents can enter review",
                status_code=status.HTTP_400_BAD_REQUEST,
                error="DOCUMENT_NOT_PENDING",
            )

    def _ensure_decidable(self, document):
        if document.status == Document.Status.APPROVED:
            raise SecureDocsException(
                "Approved documents cannot be reviewed again",
                status_code=status.HTTP_400_BAD_REQUEST,
                error="DOCUMENT_ALREADY_APPROVED",
            )
        if document.status == Document.Status.REJECTED:
            raise SecureDocsException(
                "Rejected documents cannot be reviewed again",
                status_code=status.HTTP_400_BAD_REQUEST,
                error="DOCUMENT_ALREADY_REJECTED",
            )

    def _apply_review_state(self, document, reviewer, next_status, review_notes):
        # Reviewer metadata is written with the decision so the audit trail stays attached.
        document.status = next_status
        document.reviewed_by = reviewer
        document.reviewed_at = timezone.now()
        document.review_notes = review_notes
        document.save(
            update_fields=(
                "status",
                "reviewed_by",
                "reviewed_at",
                "review_notes",
                "updated_at",
            )
        )


@extend_schema_view(
    list=extend_schema(
        summary="List categories",
        description="Return all document categories.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Categories fetched successfully",
                examples=[
                    OpenApiExample(
                        "Categories fetched response",
                        value={
                            "success": True,
                            "message": "Categories fetched successfully",
                            "data": CATEGORY_LIST_EXAMPLE,
                        },
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Categories fetched response",
                value={
                    "success": True,
                    "message": "Categories fetched successfully",
                    "data": CATEGORY_LIST_EXAMPLE,
                },
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        summary="Create category",
        description="Create a document category.",
        examples=[
            OpenApiExample(
                "Category create request",
                value={
                    "name": "Certificates",
                    "description": "Academic and professional certificates",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Category created response",
                value={
                    "success": True,
                    "message": "Category created successfully",
                    "data": CATEGORY_EXAMPLE,
                },
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get category",
        description="Return one document category.",
        examples=[
            OpenApiExample(
                "Category fetched response",
                value={
                    "success": True,
                    "message": "Category fetched successfully",
                    "data": CATEGORY_EXAMPLE,
                },
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Update category",
        description="Replace category fields.",
        examples=[
            OpenApiExample(
                "Category update request",
                value={
                    "name": "Academic Certificates",
                    "description": "Academic certificates and transcripts",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Category updated response",
                value={
                    "success": True,
                    "message": "Category updated successfully",
                    "data": {
                        **CATEGORY_EXAMPLE,
                        "name": "Academic Certificates",
                        "description": "Academic certificates and transcripts",
                    },
                },
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Partially update category",
        description="Update one or more category fields.",
        examples=[
            OpenApiExample(
                "Category patch request",
                value={
                    "description": "Academic certificates and transcripts",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Category patched response",
                value={
                    "success": True,
                    "message": "Category updated successfully",
                    "data": {
                        **CATEGORY_EXAMPLE,
                        "description": "Academic certificates and transcripts",
                    },
                },
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Delete category",
        description="Delete one category.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Category deleted successfully",
                examples=[
                    OpenApiExample(
                        "Category deleted response",
                        value={
                            "success": True,
                            "message": "Category deleted successfully",
                            "data": None,
                        },
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Category deleted response",
                value={
                    "success": True,
                    "message": "Category deleted successfully",
                    "data": None,
                },
                response_only=True,
            ),
        ],
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    response_messages = {
        "list": "Categories fetched successfully",
        "create": "Category created successfully",
        "retrieve": "Category fetched successfully",
        "update": "Category updated successfully",
        "partial_update": "Category updated successfully",
        "destroy": "Category deleted successfully",
    }

    def destroy(self, request, *args, **kwargs):
        # Keep delete responses consistent with the project's response envelope.
        super().destroy(request, *args, **kwargs)
        return Response(None, status=status.HTTP_200_OK)
