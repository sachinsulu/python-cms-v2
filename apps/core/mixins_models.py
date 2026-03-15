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
        ordering = ['position']


class SlugMixin(models.Model):
    slug = models.SlugField(blank=True, db_index=True)

    class Meta:
        abstract = True


class SEOMixin(models.Model):
    """Meta title, description, and keywords for search engines."""
    meta_title       = models.CharField(max_length=60, blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords    = models.CharField(max_length=205, blank=True)

    class Meta:
        abstract = True
