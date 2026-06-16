from rest_framework import serializers

from documents.models import Category, Document


class DocumentSerializer(serializers.ModelSerializer):
    """Full document representation returned by read and workflow endpoints."""

    uploaded_by_email = serializers.EmailField(
        source="uploaded_by.email",
        read_only=True,
    )
    reviewed_by_email = serializers.EmailField(
        source="reviewed_by.email",
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
            "reviewed_by",
            "reviewed_by_email",
            "reviewed_at",
            "review_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "verification_code",
            "status",
            "uploaded_by",
            "uploaded_by_email",
            "reviewed_by",
            "reviewed_by_email",
            "reviewed_at",
            "review_notes",
            "created_at",
            "updated_at",
        )


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Request serializer for uploads and patches; server-managed fields stay hidden."""

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


class DocumentReviewSerializer(serializers.Serializer):
    """Command payload for the single document review endpoint."""

    START_REVIEW = "START_REVIEW"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ACTION_CHOICES = (
        (START_REVIEW, "Start review"),
        (APPROVE, "Approve"),
        (REJECT, "Reject"),
    )

    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    review_notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        # Rejections need a reason because the notes become the reviewer audit trail.
        if attrs["action"] == self.REJECT and not attrs.get("review_notes"):
            raise serializers.ValidationError(
                {"review_notes": "Review notes are required when rejecting a document."}
            )

        return attrs


class PublicDocumentVerificationSerializer(serializers.ModelSerializer):
    """Safe public response for verification-code lookups."""

    verified = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "verified",
            "title",
            "document_type",
            "verification_code",
            "status",
            "reviewed_at",
        )
        read_only_fields = fields

    def get_verified(self, obj) -> bool:
        return obj.status == Document.Status.APPROVED


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description", "created_at")
        read_only_fields = ("id", "created_at")
