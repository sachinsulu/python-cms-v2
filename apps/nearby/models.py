from django.db import models
from apps.core.models import SimpleContentModel


class Nearby(SimpleContentModel):
    # Changed from CharField(max_length=255) to URLField(max_length=2048).
    # Google Maps share/embed URLs regularly exceed 255 characters.
    # URLField adds Django-level format validation on form submission.
    # Stored as VARCHAR in all backends — no data migration required.
    map_link = models.URLField(max_length=2048, blank=True)
    content   = models.TextField(blank=True)
    distance  = models.CharField(max_length=255, blank=True)
   
    class Meta(SimpleContentModel.Meta):
        verbose_name        = 'Nearby'
        verbose_name_plural = 'Nearby'
