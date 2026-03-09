from django.db import models
from apps.core.models import SimpleContentModel


class Testimonial(SimpleContentModel):
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

    class Meta(SimpleContentModel.Meta):
        verbose_name_plural = 'Testimonials'
