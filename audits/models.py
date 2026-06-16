from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED", "Document uploaded"
        DOCUMENT_DELETED = "DOCUMENT_DELETED", "Document deleted"
        DOCUMENT_REVIEW_STARTED = "DOCUMENT_REVIEW_STARTED", "Document review started"
        DOCUMENT_APPROVED = "DOCUMENT_APPROVED", "Document approved"
        DOCUMENT_REJECTED = "DOCUMENT_REJECTED", "Document rejected"
        DOCUMENT_VERIFICATION_SUCCEEDED = (
            "DOCUMENT_VERIFICATION_SUCCEEDED",
            "Document verification succeeded",
        )
        DOCUMENT_VERIFICATION_FAILED = (
            "DOCUMENT_VERIFICATION_FAILED",
            "Document verification failed",
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=80, choices=Action.choices)
    entity = models.CharField(max_length=80)
    entity_id = models.PositiveBigIntegerField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = (
            models.Index(fields=("entity", "entity_id")),
            models.Index(fields=("action",)),
            models.Index(fields=("created_at",)),
        )

    def __str__(self):
        return f"{self.action} {self.entity}#{self.entity_id}"
