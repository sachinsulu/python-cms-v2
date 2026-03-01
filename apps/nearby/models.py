from django.db import models
from django.conf import settings
from apps.core.models import BaseContentModel


class Nearby(BaseContentModel):
    map_link  = models.CharField(max_length=255, blank=True)
    content   = models.TextField(blank=True)
    distance  = models.CharField(max_length=255, blank=True)
   
    class Meta(BaseContentModel.Meta):
        verbose_name        = 'Nearby'
        verbose_name_plural = 'Nearby'
