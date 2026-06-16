from django.contrib import admin

from audits.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "entity", "entity_id", "user", "created_at")
    list_filter = ("action", "entity", "created_at")
    search_fields = ("action", "entity", "=entity_id", "user__email")
    readonly_fields = (
        "user",
        "action",
        "entity",
        "entity_id",
        "metadata",
        "created_at",
    )
