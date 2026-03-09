from django.db import models
from django.conf import settings
from apps.core.models import SimpleContentModel


class Nearby(SimpleContentModel):
    map_link  = models.CharField(max_length=255, blank=True)
    content   = models.TextField(blank=True)
    distance  = models.CharField(max_length=255, blank=True)
   
    class Meta(SimpleContentModel.Meta):
        verbose_name        = 'Nearby'
        verbose_name_plural = 'Nearby'
