"""
apps/core/querysets/base.py
============================
Reusable QuerySet classes for CMS content models.

Hierarchy:
    ActiveQuerySet   — is_active toggling (usable by any model with is_active)
    ContentQuerySet  — extends ActiveQuerySet with ordering, API, and draft helpers
                       (usable by any model with is_active + position + updated_at)

Usage in a model:
    from apps.core.querysets.base import ContentQuerySet

    class Article(BaseContentModel):
        objects = ContentQuerySet.as_manager()

All methods are chainable. No model-specific logic lives here.
"""

__all__ = [
    "ActiveQuerySet",
    "ContentQuerySet",
]

from django.db import models


class ActiveQuerySet(models.QuerySet):
    """
    Minimal QuerySet for any model that carries an `is_active` boolean.
    Safe to use on models that don't inherit from BaseContentModel
    (e.g. MediaAsset, SimpleContentModel subclasses).
    """

    def active(self):
        """Return only records where is_active=True."""
        return self.filter(is_active=True)

    def inactive(self):
        """Return only records where is_active=False."""
        return self.filter(is_active=False)


class ContentQuerySet(ActiveQuerySet):
    """
    Full-featured QuerySet for BaseContentModel subclasses.
    Assumes the model has: is_active, position, updated_at.

    Extends ActiveQuerySet with ordering, API projection, and draft helpers.
    All methods return QuerySets — slicing and limits are the caller's concern.
    """

    def published(self):
        """
        Active records in display order.
        Canonical queryset for frontend/API consumption.
        """
        return self.active().by_position()

    def draft(self):
        """
        Inactive records — items toggled off by editors.
        Useful for admin list views that want to show hidden content.
        """
        return self.inactive().by_position()

    def by_position(self):
        """
        Apply the standard CMS sort: position ASC, pk ASC as tiebreaker.
        The pk tiebreaker gives stable pagination when two records share
        the same position (e.g. after bulk imports or before a reorder).
        Overrides any prior ordering on the queryset.
        """
        return self.order_by("position", "pk")

    def recent(self):
        """
        Most recently updated records, newest first.
        Does not slice — callers apply their own limit:
            Article.objects.recent()[:10]
        """
        return self.order_by("-updated_at")

    def for_api(self):
        """
        Queryset suitable for DRF serialization:
          - active records only
          - stable display order
          - defers SEO fields not needed for list endpoints (where present)

        Uses model._meta.fields (concrete fields only) to guard against
        FieldError on models that don't carry SEO columns (e.g. MediaAsset).

        Callers should chain .select_related() / .prefetch_related()
        for FK fields specific to their model.
        """
        qs = self.published()

        if self.model is None:
            return qs

        concrete_fields = {f.name for f in self.model._meta.fields}

        defer_fields = [
            f
            for f in ("meta_title", "meta_description", "meta_keywords")
            if f in concrete_fields
        ]

        if defer_fields:
            qs = qs.defer(*defer_fields)

        return qs
