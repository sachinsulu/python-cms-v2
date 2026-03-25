from django.conf import settings
from django.db import models, transaction
from django.utils.text import slugify

from .mixins_models import (
    ActiveMixin,
    SEOMixin,
    SlugMixin,
    SortableMixin,
    TimestampMixin,
)
from .querysets.base import ActiveQuerySet, ContentQuerySet


class GlobalSlug(models.Model):
    """
    Single source of truth for slug uniqueness across all content models.

    slug       — the slug string, PK — DB-enforced unique at the schema level
    model_name — e.g. 'Article', 'Blog', 'Package'
    object_id  — PK of the owning content object

    Maintained automatically by BaseContentModel.save() and .delete().
    Never write to this table directly from application code.
    """

    slug = models.SlugField(primary_key=True, max_length=255)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Global Slug"
        verbose_name_plural = "Global Slugs"
        indexes = [
            models.Index(
                fields=["model_name", "object_id"],
                name="core_globalslug_model_obj_idx",
            ),
        ]

    def __str__(self):
        return f"{self.slug} → {self.model_name}:{self.object_id}"


class BaseContentModel(
    TimestampMixin, ActiveMixin, SortableMixin, SlugMixin, SEOMixin, models.Model
):
    """
    Abstract base for all CMS content types.

    Composes from mixins:
    - TimestampMixin  → created_at, updated_at
    - ActiveMixin     → is_active
    - SortableMixin   → position
    - SlugMixin       → slug
    - SEOMixin        → meta_title, meta_description, meta_keywords

    Adds:
    - title (required)
    - Auto slug generation
    - Atomic position assignment
    - GlobalSlug maintenance (upsert on save, delete on signal)
    - ContentQuerySet as default manager (.published(), .draft(),
      .by_position(), .recent(), .for_api())

    Slug uniqueness strategy (three layers):
      1. Form layer  — SlugUniqueMixin.clean_slug() does ONE query against
                       GlobalSlug before the user sees the save button.
      2. Save layer  — save() upserts into GlobalSlug inside the same
                       transaction, so stale data never persists.
      3. DB layer    — GlobalSlug.slug is a PK (unique), so a race condition
                       between two simultaneous saves raises IntegrityError
                       rather than silently corrupting data.

    clean() is intentionally absent — slug validation belongs in the
    form layer, not the model layer.

    Partial save contract (update_fields):
    ----------------------------------------
    Calling save(update_fields=[...]) short-circuits the full save path —
    position assignment, slug generation, and GlobalSlug maintenance are
    all skipped. This is intentional and safe ONLY for fields that do not
    influence the slug or GlobalSlug invariants (e.g. is_active, position).

    Fields in IMMUTABLE_ON_PARTIAL are protected: passing them inside
    update_fields raises ValueError immediately rather than silently
    corrupting the GlobalSlug table or leaving slug/title out of sync.

    Subclasses that derive slug from fields beyond 'title' should extend
    the set at the class level:
        class Room(BaseContentModel):
            IMMUTABLE_ON_PARTIAL = BaseContentModel.IMMUTABLE_ON_PARTIAL | {'room_number'}
    """

    # Fields whose presence in save(update_fields=...) is forbidden.
    # Both influence slug generation and/or GlobalSlug integrity and must
    # always go through the full save path.
    IMMUTABLE_ON_PARTIAL: frozenset = frozenset({"slug", "title"})

    # ContentQuerySet gives every concrete subclass .published(), .draft(),
    # .by_position(), .recent(), and .for_api() as first-class manager methods.
    # Standard ORM methods (.filter(), .get(), .only(), etc.) are unaffected.
    objects = ContentQuerySet.as_manager()

    title = models.CharField(max_length=255)

    class Meta:
        abstract = True
        ordering = ["position"]

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")

        if update_fields is not None:
            # ----------------------------------------------------------------
            # Partial save — fast path.
            #
            # Skips: position assignment, slug auto-generation, GlobalSlug
            # upsert, and the transaction.atomic() wrapper. Safe because none
            # of those invariants change when only non-slug fields are updated
            # (e.g. toggle_status passing update_fields=['is_active']).
            #
            # Guard: reject any update_fields list that contains a field whose
            # mutation has side-effects on the slug or GlobalSlug table. A
            # ValueError here is intentional — silent data corruption is worse
            # than a loud crash during development.
            # ----------------------------------------------------------------
            unsafe = self.IMMUTABLE_ON_PARTIAL.intersection(update_fields)
            if unsafe:
                raise ValueError(
                    f"{self.__class__.__name__}.save(update_fields=...) "
                    f"cannot include {sorted(unsafe)!r}. "
                    "These fields have side-effects (slug generation, GlobalSlug "
                    "sync) that require the full save() path. "
                    "Call save() without update_fields instead."
                )
            super().save(*args, **kwargs)
            return

        # Full save path — all invariants enforced inside one atomic block.
        with transaction.atomic():
            self._assign_position()

            if not self.slug:
                self.slug = slugify(self.title, allow_unicode=True)

            old_slug = None
            if self.pk:
                try:
                    old_slug = (
                        self.__class__._default_manager
                        .only("slug")
                        .get(pk=self.pk)
                        .slug
                    )
                except self.__class__.DoesNotExist:
                    pass

            super().save(*args, **kwargs)

            if old_slug and old_slug != self.slug:
                GlobalSlug.objects.filter(slug=old_slug).delete()

            # Upsert GlobalSlug in the same transaction.
            # update_or_create handles both new objects and slug-unchanged edits.
            GlobalSlug.objects.update_or_create(
                slug=self.slug,
                defaults={
                    "model_name": self.__class__.__name__,
                    "object_id": self.pk,
                },
            )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super().delete(*args, **kwargs)

    def __str__(self):
        return self.title


class SimpleContentModel(TimestampMixin, ActiveMixin, SortableMixin, models.Model):
    """
    Lightweight base for CMS models that don't need SEO or slugs.
    No GlobalSlug involvement — these models carry no slug field.

    Uses ContentQuerySet as default manager so .published(), .draft(),
    .by_position(), and .recent() are available on all subclasses without
    any per-model boilerplate.

    Partial save contract:
    ----------------------
    save(update_fields=[...]) short-circuits position assignment and the
    atomic wrapper. Safe for all field combinations — SimpleContentModel
    has no slug or GlobalSlug invariants to protect.
    """

    objects = ContentQuerySet.as_manager()

    title = models.CharField(max_length=255)

    class Meta:
        abstract = True
        ordering = ["position"]

    def save(self, *args, **kwargs):
        # Partial saves (e.g. toggle_status) skip position assignment and the
        # atomic wrapper — position does not change on field-specific updates,
        # and there are no slug invariants to enforce on this base class.
        if kwargs.get("update_fields") is not None:
            super().save(*args, **kwargs)
            return

        with transaction.atomic():
            self._assign_position()
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ------------------------------------------------------------------ #
# Audit Log
# ------------------------------------------------------------------ #


class AuditLog(models.Model):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BULK_DELETE = "bulk_delete"
    TOGGLE = "toggle"
    BULK_TOGGLE = "bulk_toggle"
    REORDER = "reorder"

    ACTION_CHOICES = [
        (CREATE, "Create"),
        (UPDATE, "Update"),
        (DELETE, "Delete"),
        (BULK_DELETE, "Bulk Delete"),
        (TOGGLE, "Toggle Status"),
        (BULK_TOGGLE, "Bulk Toggle"),
        (REORDER, "Reorder"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, db_index=True)
    object_id = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["model_name", "object_id"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["timestamp"], name="core_auditlog_timestamp_idx"),
        ]

    def __str__(self):
        user = self.user.username if self.user else "system"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {user} {self.action} {self.model_name}:{self.object_id}"


def _remove_global_slug(sender, instance, **kwargs):
    """
    Remove the GlobalSlug row when a BaseContentModel instance is deleted.

    Handles both QuerySet.delete() (bulk deletes) and instance.delete().

    Not decorated with @receiver — connected selectively in CoreConfig.ready()
    only for concrete BaseContentModel subclasses, so it never fires on
    unrelated models (e.g. User, MediaAsset, Permission) and never pays the
    cost of the isinstance() guard on every post_delete signal in the project.
    """
    if hasattr(instance, "slug") and instance.slug:
        GlobalSlug.objects.filter(slug=instance.slug).delete()