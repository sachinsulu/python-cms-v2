from django.db import models
from django.conf import settings
from apps.core.models import BaseContentModel


class Article(BaseContentModel):
    subtitle  = models.CharField(max_length=255, blank=True)
    content   = models.TextField(blank=False)
    image     = models.ImageField(upload_to='articles/', blank=True, null=True)
    homepage  = models.BooleanField(default=False, db_index=True,
                    help_text='Show on homepage instead of inner pages')
    author    = models.ForeignKey(
                    settings.AUTH_USER_MODEL,
                    null=True, blank=True,
                    on_delete=models.SET_NULL,
                    related_name='articles'
                )

    class Meta(BaseContentModel.Meta):
        verbose_name        = 'Article'
        verbose_name_plural = 'Articles'
