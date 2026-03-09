from django.db import models, transaction
from django.db.models import Max
from django.conf import settings
from django.utils.text import slugify

from .mixins_models import TimestampMixin, ActiveMixin, SortableMixin, SlugMixin, SEOMixin


class BaseContentModel(TimestampMixin, ActiveMixin, SortableMixin, SlugMixin, SEOMixin, models.Model):
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
    - Auto slug generation (cross-model unique via registry)
    - Atomic position assignment
    """
    title = models.CharField(max_length=255)

    class Meta:
        abstract = True
        ordering = ['position']

    # ------------------------------------------------------------------ #
    # Slug generation
    # ------------------------------------------------------------------ #

    def clean(self):
        super().clean()
        from .registry import cms_registry
        from django.core.exceptions import ValidationError

        target_slug = self.slug
        if not target_slug and self.title:
            target_slug = slugify(self.title, allow_unicode=True)

        if target_slug and cms_registry.is_slug_taken(target_slug, exclude_obj=self):
            raise ValidationError(f"The slug '{target_slug}' already exists. Please use a unique title or edit the slug manually.")

    # ------------------------------------------------------------------ #
    # Save with atomic position + slug logic
    # ------------------------------------------------------------------ #

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Auto-assign position only on creation, not on every save
            if not self.pk:
                last = (
                    self.__class__.objects
                    .select_for_update()
                    .aggregate(Max('position'))['position__max']
                )
                self.position = (last or 0) + 1

            # Auto-generate slug from title
            if not self.slug:
                self.slug = slugify(self.title, allow_unicode=True)

            super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ------------------------------------------------------------------ #
# Audit Log
# ------------------------------------------------------------------ #

class AuditLog(models.Model):
    CREATE      = 'create'
    UPDATE      = 'update'
    DELETE      = 'delete'
    BULK_DELETE = 'bulk_delete'
    TOGGLE      = 'toggle'
    BULK_TOGGLE = 'bulk_toggle'
    REORDER     = 'reorder'

    ACTION_CHOICES = [
        (CREATE,      'Create'),
        (UPDATE,      'Update'),
        (DELETE,      'Delete'),
        (BULK_DELETE, 'Bulk Delete'),
        (TOGGLE,      'Toggle Status'),
        (BULK_TOGGLE, 'Bulk Toggle'),
        (REORDER,     'Reorder'),
    ]

    user        = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      null=True, blank=True,
                      on_delete=models.SET_NULL,
                      related_name='audit_logs'
                  )
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name  = models.CharField(max_length=100, db_index=True)
    object_id   = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255)
    changes     = models.JSONField(default=dict)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes  = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        user = self.user.username if self.user else 'system'
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {user} {self.action} {self.model_name}:{self.object_id}"
