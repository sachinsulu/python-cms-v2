"""
apps/core/services/slug_service.py
====================================
Slug uniqueness helpers — extracted from CMSRegistry.

Public interface:
    is_slug_taken(slug, exclude_obj=None) -> bool

CMSRegistry.is_slug_taken() delegates to this function so all callers
that go through the registry continue to work without changes.
"""

__all__ = ["is_slug_taken"]


def is_slug_taken(slug: str, exclude_obj=None) -> bool:
    """
    Returns True if ``slug`` already exists in GlobalSlug.

    One DB query regardless of how many content models are registered.

    Args:
        slug:        The slug string to check.
        exclude_obj: Pass the current instance when editing so its own
                     GlobalSlug row is not counted as a conflict.
    """
    from apps.core.models import GlobalSlug  # local import — avoids circular

    qs = GlobalSlug.objects.filter(slug=slug)

    if exclude_obj is not None and getattr(exclude_obj, "pk", None):
        qs = qs.exclude(
            model_name=exclude_obj.__class__.__name__,
            object_id=exclude_obj.pk,
        )

    return qs.exists()
