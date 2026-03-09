from django.db import models
from django.conf import settings
from apps.core.models import BaseContentModel


class FAQ(BaseContentModel):
    content   = models.TextField(blank=True)
    
    class Meta(BaseContentModel.Meta):
        verbose_name        = 'FAQ'
        verbose_name_plural = 'FAQS'
