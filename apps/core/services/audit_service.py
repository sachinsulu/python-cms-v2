"""
apps/core/services/audit_service.py
=====================================
Audit helpers — extracted from apps/core/audit.py.

Public interface (unchanged):
    get_client_ip(request)                                    -> str | None
    log_action(request, action, obj, changes=None)            -> AuditLog
    log_bulk_action(request, action, model_name, count, ids)  -> None
"""

import logging

logger = logging.getLogger("cms.audit")

__all__ = [
    "get_client_ip",
    "log_action",
    "log_bulk_action",
]


def get_client_ip(request) -> str | None:
    """Return the real client IP, respecting X-Forwarded-For."""
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or None


def log_action(request, action: str, obj, changes: dict = None):
    """
    Create an AuditLog entry and emit a structured log line.

    Usage:
        from apps.core.services.audit_service import log_action
        from apps.core.models import AuditLog
        log_action(request, AuditLog.CREATE, article)
        log_action(request, AuditLog.UPDATE, article, changes={'before': {...}, 'after': {...}})
    """
    from apps.core.models import (
        AuditLog,  # local import — avoids circular at module level
    )

    entry = AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        model_name=obj.__class__.__name__,
        object_id=str(obj.pk),
        object_repr=str(obj)[:255],
        changes=changes or {},
        ip_address=get_client_ip(request),
    )
    logger.info(
        "AUDIT user=%s action=%s model=%s pk=%s",
        entry.user,
        action,
        entry.model_name,
        entry.object_id,
    )
    return entry


def log_bulk_action(request, action: str, model_name: str, count: int, ids: list):
    """For bulk operations that don't have a single object."""
    from apps.core.models import (
        AuditLog,  # local import — avoids circular at module level
    )

    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        model_name=model_name,
        object_id="bulk",
        object_repr=f"{count} {model_name}(s)",
        changes={"ids": ids, "count": count},
        ip_address=get_client_ip(request),
    )
    logger.info(
        "AUDIT user=%s action=%s model=%s count=%d",
        request.user,
        action,
        model_name,
        count,
    )
