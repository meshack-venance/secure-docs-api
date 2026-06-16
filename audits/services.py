from audits.models import AuditLog


def write_audit_log(user, action, entity, entity_id, metadata=None):
    """Record one business event without spreading AuditLog creation across views."""
    return AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        metadata=metadata or {},
    )
