from django.contrib import admin

from documents.models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "verification_code",
        "uploaded_by",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("title", "description", "verification_code", "uploaded_by__email")
    readonly_fields = ("verification_code", "created_at", "updated_at")
