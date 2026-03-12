import os
import logging
import threading
from io import BytesIO
from pathlib import Path

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile

from apps.core.mixins_models import TimestampMixin, ActiveMixin

logger = logging.getLogger(__name__)


class MediaAsset(TimestampMixin, ActiveMixin, models.Model):
    """
    Centralized media library asset.
    All content models reference this via ForeignKey.

    Thumbnail generation is offloaded to a daemon thread after the initial
    save so the upload response returns immediately. The thread re-fetches
    the instance by pk to avoid sharing state with the request thread.
    """
    IMAGE = 'image'
    FILE  = 'file'
    VIDEO = 'video'

    FILE_TYPES = [
        (IMAGE, 'Image'),
        (FILE,  'File'),
        (VIDEO, 'Video'),
    ]

    EXTENSION_MAP = {
        'jpg': IMAGE, 'jpeg': IMAGE, 'png': IMAGE,
        'gif': IMAGE, 'webp': IMAGE, 'svg': IMAGE,
        'heic': IMAGE, 'bmp': IMAGE, 'ico': IMAGE,
        'mp4': VIDEO, 'mov': VIDEO, 'avi': VIDEO,
        'mkv': VIDEO, 'webm': VIDEO,
    }

    file      = models.FileField(upload_to='media-library/%Y/%m/')
    file_type = models.CharField(
        max_length=20, choices=FILE_TYPES, default=FILE, db_index=True,
    )
    alt_text  = models.CharField(max_length=255, blank=True)
    width     = models.PositiveIntegerField(null=True, blank=True)
    height    = models.PositiveIntegerField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='media-library/thumbs/', blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='media_assets',
    )

    class Meta:
        ordering            = ['-created_at']
        verbose_name        = 'Media Asset'
        verbose_name_plural = 'Media Assets'

    def __str__(self):
        return self.alt_text or (
            os.path.basename(self.file.name) if self.file else 'Untitled Asset'
        )

    def save(self, *args, **kwargs):
        if self.file:
            ext = self.file.name.rsplit('.', 1)[-1].lower() if '.' in self.file.name else ''
            self.file_type = self.EXTENSION_MAP.get(ext, self.FILE)

        super().save(*args, **kwargs)

        # Only spawn the thread for new image uploads that don't yet have a
        # thumbnail. update_fields saves (e.g. the thread's own write-back)
        # are excluded to prevent an infinite loop.
        is_partial_update = kwargs.get('update_fields') is not None
        if (
            not is_partial_update
            and self.file_type == self.IMAGE
            and self.file
            and not self.thumbnail
        ):
            t = threading.Thread(
                target=MediaAsset._generate_thumbnail_async,
                args=(self.pk,),
                daemon=True,
            )
            t.start()

    @staticmethod
    def _generate_thumbnail_async(pk: int) -> None:
        """
        Runs in a background daemon thread.
        Re-fetches the instance by pk for a clean DB connection,
        then writes dimensions + WebP thumbnail back via update_fields.
        """
        try:
            instance = MediaAsset.objects.get(pk=pk)
        except MediaAsset.DoesNotExist:
            return

        if instance.thumbnail:
            return  # already done (duplicate thread guard)

        try:
            from PIL import Image as PILImage

            img  = PILImage.open(instance.file.path)
            w, h = img.size
            updated = []

            if instance.width != w or instance.height != h:
                instance.width  = w
                instance.height = h
                updated.extend(['width', 'height'])

            if instance._make_thumbnail(img):
                updated.append('thumbnail')

            if updated:
                instance.save(update_fields=updated)

        except Exception as exc:
            logger.warning('Thumbnail generation failed pk=%s: %s', pk, exc)

    def _make_thumbnail(self, img, size=(600, 400), quality=85) -> bool:
        try:
            thumb = img.copy()
            thumb.thumbnail(size)

            if thumb.mode in ('P', 'PA'):
                thumb = thumb.convert('RGBA')
            if thumb.mode not in ('RGB', 'RGBA'):
                thumb = thumb.convert('RGB')

            buffer   = BytesIO()
            thumb.save(buffer, format='WEBP', quality=quality)
            stem     = Path(self.file.name).stem
            filename = f'{stem}_{self.pk}.webp'
            self.thumbnail.save(filename, ContentFile(buffer.getvalue()), save=False)
            return True

        except Exception as exc:
            logger.warning('_make_thumbnail failed pk=%s: %s', self.pk, exc)
            return False

    @property
    def url(self):
        return self.file.url if self.file else ''

    @property
    def thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else self.url

    @property
    def is_image(self):
        return self.file_type == self.IMAGE
