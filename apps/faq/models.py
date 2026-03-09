from django.db import models
from django.conf import settings
from apps.core.models import SimpleContentModel


class FAQ(SimpleContentModel):
    content   = models.TextField(blank=True)
    
    class Meta(SimpleContentModel.Meta):
        verbose_name        = 'FAQ'
        verbose_name_plural = 'FAQS'
