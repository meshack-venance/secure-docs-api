from rest_framework import serializers

from documents.models import Document


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
