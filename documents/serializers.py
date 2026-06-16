from rest_framework import serializers

from documents.models import Category, Document


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


class DocumentCreateSerializer(serializers.ModelSerializer):
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
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "verification_code",
            "status",
            "created_at",
            "updated_at",
        )
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description", "created_at")
        read_only_fields = ("id", "created_at")
