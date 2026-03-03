from django.db import models
from apps.core.models import BaseContentModel


class Testimonial(BaseContentModel):
    name     = models.CharField(max_length=255)
    content  = models.TextField()
    rating   = models.PositiveSmallIntegerField(default=5)
    image    = models.ForeignKey(
                   'media.MediaAsset', on_delete=models.SET_NULL,
                   null=True, blank=True, related_name='testimonials',
               )
    country  = models.CharField(max_length=100, blank=True)
    linksrc  = models.CharField(max_length=500, blank=True)
    via_type = models.CharField(max_length=100, blank=True)

    class Meta(BaseContentModel.Meta):
        verbose_name_plural = 'Testimonials'
