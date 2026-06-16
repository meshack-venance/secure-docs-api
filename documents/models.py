import secrets
import string

from django.conf import settings
from django.db import models


def generate_verification_code():
    """Generate public-facing codes that are short enough to type manually."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(9))


class Document(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    document_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    verification_code = models.CharField(max_length=12, unique=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_documents",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        # The verification code is assigned once so public links stay stable.
        if not self.verification_code:
            self.verification_code = self._generate_unique_verification_code()

        super().save(*args, **kwargs)

    @classmethod
    def _generate_unique_verification_code(cls):
        # Collisions are unlikely, but the database uniqueness rule still wins.
        while True:
            code = generate_verification_code()
            if not cls.objects.filter(verification_code=code).exists():
                return code

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
