import os
import logging
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
    All content models link here instead of storing their own ImageField.
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

    file = models.FileField(upload_to='media-library/%Y/%m/')
    file_type = models.CharField(
        max_length=20, choices=FILE_TYPES, default=FILE, db_index=True,
    )
    alt_text = models.CharField(max_length=255, blank=True)

    # Auto-populated for images
    width  = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    # WebP thumbnail (auto-generated for images)
    thumbnail = models.ImageField(
        upload_to='media-library/thumbs/', blank=True,
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='media_assets',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Media Asset'
        verbose_name_plural = 'Media Assets'

    def __str__(self):
        return self.alt_text or os.path.basename(self.file.name)

    # ------------------------------------------------------------------ #
    # Auto-detect + thumbnail generation
    # ------------------------------------------------------------------ #

    def save(self, *args, **kwargs):
        # Auto-detect file type from extension
        if self.file:
            ext = self.file.name.rsplit('.', 1)[-1].lower()
            self.file_type = self.EXTENSION_MAP.get(ext, self.FILE)

        super().save(*args, **kwargs)

        # For images: extract dimensions + generate WebP thumbnail
        if self.file_type == self.IMAGE and self.file:
            updated = []
            try:
                from PIL import Image

                img = Image.open(self.file.path)
                w, h = img.size

                if self.width != w or self.height != h:
                    self.width = w
                    self.height = h
                    updated.extend(['width', 'height'])

                # Generate WebP thumbnail if not yet created
                if not self.thumbnail:
                    thumb = self._make_thumbnail(img)
                    if thumb:
                        updated.append('thumbnail')

            except Exception as e:
                logger.warning('MediaAsset image processing failed (pk=%s): %s', self.pk, e)

            if updated:
                super().save(update_fields=updated)

    def _make_thumbnail(self, img, size=(600, 400), quality=85):
        """Generate a WebP thumbnail from a PIL Image."""
        try:
            thumb = img.copy()
            thumb.thumbnail(size)

            # Convert palette / RGBA modes for WebP compatibility
            if thumb.mode in ('P', 'PA'):
                thumb = thumb.convert('RGBA')
            if thumb.mode == 'RGBA':
                # WebP supports RGBA, keep it
                pass
            elif thumb.mode != 'RGB':
                thumb = thumb.convert('RGB')

            buffer = BytesIO()
            thumb.save(buffer, format='WEBP', quality=quality)

            stem = Path(self.file.name).stem
            filename = f'{stem}_{self.pk}.webp'

            self.thumbnail.save(filename, ContentFile(buffer.getvalue()), save=False)
            return True
        except Exception as e:
            logger.warning('Thumbnail generation failed (pk=%s): %s', self.pk, e)
            return False

    @property
    def url(self):
        return self.file.url if self.file else ''

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return self.url

    @property
    def is_image(self):
        return self.file_type == self.IMAGE
