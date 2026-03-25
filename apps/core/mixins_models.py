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

    def _assign_position(self, scope_qs=None):
        """
        Sets position to max(existing_in_scope) + 1 for new instances.

        No-op conditions — skips assignment when any of these are true:
          1. self.pk is set    → existing instance, position already persisted.
          2. self.position > 0 → caller has already set a specific position
                                  (used by SubPackage.save() to pass a
                                  scoped value before delegating to super()).

        Must be called inside an atomic block — BaseContentModel.save() and
        SimpleContentModel.save() both guarantee this via transaction.atomic().

        Race-condition fix (replaces the previous select_for_update+aggregate):
        -----------------------------------------------------------------------
        The original code used:
            .select_for_update().aggregate(Max("position"))

        select_for_update() on an aggregate does NOT acquire row locks on
        PostgreSQL because no rows are returned — there is nothing to lock.
        Two concurrent inserts could both read the same MAX and receive
        identical positions.

        The fix locks the actual last row:
            .select_for_update().order_by('-position').first()

        This fetches and holds a row-level lock on a real row. A second
        concurrent create blocks on that lock until the first transaction
        commits, then reads the updated maximum, guaranteeing monotonically
        increasing, non-duplicate positions.

        .only('position') is intentionally omitted: the performance gain is
        negligible (the row is being locked regardless) and deferred field
        loading from .only() can cause unexpected extra queries if any
        downstream code accesses non-deferred attributes on the instance.

        scope_qs parameter:
        -------------------
        Pass a pre-filtered QuerySet to constrain the max lookup to a subset
        of rows. SubPackage.save() passes a queryset filtered to the same
        parent Package so each package maintains its own independent position
        counter starting from 1. When None, the full table is used.
        """
        if self.pk:
            # Existing instance — position is already stored in the DB.
            return

        if self.position > 0:
            # Caller has explicitly pre-set position before calling save()
            # (e.g. SubPackage.save() called _assign_position with a scoped
            # queryset and stored the result in self.position). Trust it.
            return

        qs = scope_qs if scope_qs is not None else self.__class__.objects

        # Lock the current last row so concurrent inserts serialise here.
        # .first() returns None when the table / scope is empty → position 1.
        last = (
            qs
            .select_for_update()
            .order_by('-position')
            .first()
        )
        self.position = (last.position + 1) if last else 1


class SlugMixin(models.Model):
    # db_index=True is required here even though GlobalSlug.slug (PK) is
    # already indexed. GlobalSlug is used for cross-model uniqueness checking
    # only. Actual object lookups — get_object_or_404(Article, slug=slug),
    # ContentUpdateView.get_object(), and all API slug-based detail endpoints
    # — query the model's own table directly. Without this index those
    # lookups are full table scans.
    slug = models.SlugField(blank=True, db_index=True)

    class Meta:
        abstract = True


class SEOMixin(models.Model):
    """Meta title, description, and keywords for search engines."""

    meta_title       = models.CharField(max_length=60,  blank=True)
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords    = models.CharField(max_length=205, blank=True)

    class Meta:
        abstract = True