from django.db import models
from django.conf import settings
from apps.core.models import BaseContentModel


class Blog(BaseContentModel):
    subtitle     = models.CharField(max_length=255, blank=True)
    author       = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       null=True, blank=True,
                       on_delete=models.SET_NULL,
                       related_name='blogs'
                   )
    date         = models.DateField(null=True, blank=True)
    image        = models.ImageField(upload_to='blog/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='blog/banners/', blank=True, null=True)
    content      = models.TextField(blank=True)

    class Meta(BaseContentModel.Meta):
        verbose_name        = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
