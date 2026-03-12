from django.db import models, transaction
from django.db.models import Max
from django.conf import settings
from django.utils.text import slugify

from .mixins_models import TimestampMixin, ActiveMixin, SortableMixin, SlugMixin, SEOMixin


class GlobalSlug(models.Model):
    """
    Single source of truth for slug uniqueness across all content models.

    slug       — the slug string, PK — DB-enforced unique at the schema level
    model_name — e.g. 'Article', 'Blog', 'Package'
    object_id  — PK of the owning content object

    Maintained automatically by BaseContentModel.save() and .delete().
    Never write to this table directly from application code.
    """
    slug       = models.SlugField(primary_key=True, max_length=255)
    model_name = models.CharField(max_length=100)
    object_id  = models.PositiveIntegerField()

    class Meta:
        verbose_name        = 'Global Slug'
        verbose_name_plural = 'Global Slugs'
        indexes = [
            models.Index(
                fields=['model_name', 'object_id'],
                name='core_globalslug_model_obj_idx',
            ),
        ]

    def __str__(self):
        return f'{self.slug} → {self.model_name}:{self.object_id}'


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
    - Auto slug generation
    - Atomic position assignment
    - GlobalSlug maintenance (upsert on save, delete on delete)

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
    """
    title = models.CharField(max_length=255)

    class Meta:
        abstract = True
        ordering = ['position']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                last = (
                    self.__class__.objects
                    .select_for_update()
                    .aggregate(Max('position'))['position__max']
                )
                self.position = (last or 0) + 1

            if not self.slug:
                self.slug = slugify(self.title, allow_unicode=True)

            old_slug = None
            if self.pk:
                try:
                    old_slug = self.__class__.objects.only('slug').get(pk=self.pk).slug
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
                    'model_name': self.__class__.__name__,
                    'object_id':  self.pk,
                },
            )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            GlobalSlug.objects.filter(slug=self.slug).delete()
            super().delete(*args, **kwargs)

    def __str__(self):
        return self.title


class SimpleContentModel(TimestampMixin, ActiveMixin, SortableMixin, models.Model):
    """
    Lightweight base for CMS models that don't need SEO or slugs.
    No GlobalSlug involvement — these models carry no slug field.
    """
    title = models.CharField(max_length=255)

    class Meta:
        abstract = True
        ordering = ['position']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                last = (
                    self.__class__.objects
                    .select_for_update()
                    .aggregate(Max('position'))['position__max']
                )
                self.position = (last or 0) + 1
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
                      related_name='audit_logs',
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
