from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from accounts.models import User
from common.exceptions import SecureDocsException
from documents.models import Category, Document
from documents.permissions import CanAccessDocument
from documents.serializers import CategorySerializer, DocumentCreateSerializer, DocumentSerializer


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
    "created_at": "2026-06-16T10:00:00Z",
    "updated_at": "2026-06-16T10:00:00Z",
}

DOCUMENT_UPLOAD_EXAMPLE = {
    "title": "Degree Certificate",
    "file": "<binary file>",
    "document_type": "Certificate",
    "description": "Bachelor degree certificate for Meshack Venance",
}

DOCUMENT_LIST_EXAMPLE = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [DOCUMENT_EXAMPLE],
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
    "errors": {
        "detail": "Invalid document status filter",
    },
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
    update=extend_schema(
        summary="Update document",
        description="Replace editable document fields.",
        examples=[
            OpenApiExample(
                "Document update request",
                value={
                    "title": "Updated Degree Certificate",
                    "file": "<binary file>",
                    "document_type": "Certificate",
                    "description": "Updated certificate description",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Document updated response",
                value={
                    "success": True,
                    "message": "Document updated successfully",
                    "data": {
                        **DOCUMENT_EXAMPLE,
                        "title": "Updated Degree Certificate",
                        "description": "Updated certificate description",
                    },
                },
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Partially update document",
        description="Update one or more editable document fields.",
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
    queryset = Document.objects.select_related("uploaded_by")
    permission_classes = (CanAccessDocument,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("title", "description", "verification_code")
    ordering_fields = ("created_at", "updated_at", "title", "status")
    ordering = ("-created_at",)
    response_messages = {
        "list": "Documents fetched successfully",
        "create": "Document uploaded successfully",
        "retrieve": "Document fetched successfully",
        "update": "Document updated successfully",
        "partial_update": "Document updated successfully",
        "destroy": "Document deleted successfully",
    }

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

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

        return queryset.filter(uploaded_by=user)

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentCreateSerializer

        return DocumentSerializer

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(None, status=status.HTTP_200_OK)


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
        super().destroy(request, *args, **kwargs)
        return Response(None, status=status.HTTP_200_OK)
