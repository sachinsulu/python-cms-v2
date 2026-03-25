"""
apps/core/services/content_service.py
======================================
Content object lifecycle helpers — encapsulate the create/update flow so
that generic_views.py, API viewsets, and management commands all go through
a single, tested code path.

Extracted from ContentCreateView.post / ContentUpdateView.post in
apps/core/generic_views.py.  Those views continue to call these functions
rather than duplicating the three-step pattern inline.

Public interface:
    create_object(request, form, before_save_fn=None)  -> model instance
    update_object(request, form, obj, before_save_fn=None,
                  changed_fields=None)                 -> model instance

Both functions:
  1. Call before_save_fn(request, obj) if provided (e.g. to set parent FK).
  2. Call obj.save() — which triggers position assignment and GlobalSlug
     maintenance defined on BaseContentModel.
  3. Invalidate the dashboard stats/recent-items cache.
  4. Write an AuditLog entry.
  5. Return the saved instance so callers can redirect or build a response.

Raising exceptions:
  Neither function catches exceptions from obj.save().  IntegrityError (e.g.
  duplicate slug race condition) is allowed to propagate so the view layer
  can decide how to handle it.  Wrapping save() in transaction.atomic() is
  left to the caller when needed (BaseContentModel.save() already does this
  internally).
"""

from __future__ import annotations

import logging
from typing import Callable

logger = logging.getLogger(__name__)

__all__ = [
    "create_object",
    "update_object",
]


def create_object(
    request,
    form,
    before_save_fn: Callable | None = None,
):
    """
    Persist a new content object from a validated form.

    Args:
        request:        The current HTTP request (used for AuditLog and IP).
        form:           A bound, validated ModelForm.  Must already have
                        passed form.is_valid().
        before_save_fn: Optional hook called as before_save_fn(request, obj)
                        after form.save(commit=False) but before obj.save().
                        Use it to set fields the form doesn't know about
                        (e.g. the parent FK on SubPackage, the author on an
                        Article, or any flag derived from request context).

    Returns:
        The saved model instance.

    Raises:
        AssertionError: If form.is_valid() has not been called / returned False.
    """
    # Guard: callers must validate before handing the form here.
    assert form.is_valid(), (
        "create_object() received an invalid form. "
        "Call form.is_valid() and check the result before invoking this helper."
    )

    # Local imports avoid circular dependencies at module load time.
    from apps.core.cache import invalidate_dashboard_cache
    from apps.core.models import AuditLog
    from apps.core.services.audit_service import log_action

    obj = form.save(commit=False)

    if before_save_fn is not None:
        before_save_fn(request, obj)

    obj.save()

    invalidate_dashboard_cache()
    log_action(request, AuditLog.CREATE, obj)

    logger.debug(
        "content_service.create_object: %s pk=%s created by user=%s",
        obj.__class__.__name__,
        obj.pk,
        getattr(request.user, "username", "anonymous"),
    )

    return obj


def update_object(
    request,
    form,
    obj,
    before_save_fn: Callable | None = None,
    changed_fields: list[str] | None = None,
):
    """
    Persist changes to an existing content object from a validated form.

    Args:
        request:        The current HTTP request.
        form:           A bound, validated ModelForm bound to ``obj``.
        obj:            The existing model instance being updated.
        before_save_fn: Optional hook called as before_save_fn(request, updated)
                        after form.save(commit=False) but before updated.save().
        changed_fields: List of field names that changed (e.g. form.changed_data).
                        When provided, the AuditLog entry will record before/after
                        values for those fields.  When None, an empty changes dict
                        is recorded (still creates an UPDATE entry).

    Returns:
        The updated model instance (same object as ``obj``, after save).

    Raises:
        AssertionError: If form.is_valid() has not been called / returned False.
    """
    assert form.is_valid(), (
        "update_object() received an invalid form. "
        "Call form.is_valid() and check the result before invoking this helper."
    )

    from apps.core.cache import invalidate_dashboard_cache
    from apps.core.models import AuditLog
    from apps.core.services.audit_service import log_action

    # Capture before-values for changed fields while we still have the
    # pre-save state in ``obj`` (form.save(commit=False) mutates the instance).
    before_values: dict[str, str] = {}
    if changed_fields:
        before_values = {
            field: str(getattr(obj, field, ""))
            for field in changed_fields
            if hasattr(obj, field)
        }

    updated = form.save(commit=False)

    if before_save_fn is not None:
        before_save_fn(request, updated)

    updated.save()

    # Build after-values now that the instance reflects the saved state.
    after_values: dict[str, str] = {}
    if changed_fields:
        after_values = {
            field: str(getattr(updated, field, ""))
            for field in changed_fields
            if hasattr(updated, field)
        }

    changes = {"before": before_values, "after": after_values} if changed_fields else {}

    invalidate_dashboard_cache()
    log_action(request, AuditLog.UPDATE, updated, changes=changes)

    logger.debug(
        "content_service.update_object: %s pk=%s updated by user=%s fields=%s",
        updated.__class__.__name__,
        updated.pk,
        getattr(request.user, "username", "anonymous"),
        changed_fields or [],
    )

    return updated