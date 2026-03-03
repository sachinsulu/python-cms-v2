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
    image        = models.ForeignKey(
                       'media.MediaAsset', on_delete=models.SET_NULL,
                       null=True, blank=True, related_name='blogs',
                   )
    banner_image = models.ForeignKey(
                       'media.MediaAsset', on_delete=models.SET_NULL,
                       null=True, blank=True, related_name='blog_banners',
                   )
    content      = models.TextField(blank=True)

    class Meta(BaseContentModel.Meta):
        verbose_name        = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
