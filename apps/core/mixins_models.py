"""
Model Mixins
=============
Composable abstract model mixins for building CMS content types.
BaseContentModel uses all of these; other models (like MediaAsset) can
cherry-pick only what they need.
"""

from django.db import models


class TimestampMixin(models.Model):
    """Auto-managed created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    """Soft-toggle is_active flag."""

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True


class SortableMixin(models.Model):
    """Integer-based position for drag-and-drop ordering."""

    position = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["position"]

    def _assign_position(self):
        """
        Sets position to max(existing) + 1 for new instances.
        Must be called inside an atomic block (BaseContentModel.save() provides this).
        Uses select_for_update() to prevent race conditions.
        No-op when called on an existing instance (self.pk is set).
        """
        if not self.pk:
            from django.db.models import Max

            last = self.__class__.objects.select_for_update().aggregate(
                Max("position")
            )["position__max"]
            self.position = (last or 0) + 1


class SlugMixin(models.Model):
    # db_index omitted — unique=True is enforced per-model via GlobalSlug.slug
    # (which is a PK and therefore already indexed at the DB level).
    slug = models.SlugField(blank=True)

    class Meta:
        abstract = True


class SEOMixin(models.Model):
    """Meta title, description, and keywords for search engines."""

    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=205, blank=True)

    class Meta:
        abstract = True
