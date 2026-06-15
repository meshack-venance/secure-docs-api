from rest_framework import viewsets

from accounts.models import User
from documents.models import Document
from documents.permissions import CanAccessDocument
from documents.serializers import DocumentCreateSerializer, DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = (CanAccessDocument,)

    def get_queryset(self):
        user = self.request.user
        queryset = Document.objects.select_related("uploaded_by")

        if user.role in (User.Role.ADMIN, User.Role.OFFICER):
            return queryset

        return queryset.filter(uploaded_by=user)

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentCreateSerializer

        return DocumentSerializer

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
