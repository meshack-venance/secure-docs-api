from rest_framework import filters, status, viewsets
from rest_framework.response import Response

from accounts.models import User
from documents.models import Category, Document
from documents.permissions import CanAccessDocument
from documents.serializers import CategorySerializer, DocumentCreateSerializer, DocumentSerializer


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

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

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
