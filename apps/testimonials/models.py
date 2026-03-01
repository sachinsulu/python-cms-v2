from django.db import models
from apps.core.models import BaseContentModel


class Testimonial(BaseContentModel):
    name     = models.CharField(max_length=255)
    content  = models.TextField()
    rating   = models.PositiveSmallIntegerField(default=5)
    image    = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    country  = models.CharField(max_length=100, blank=True)
    linksrc  = models.CharField(max_length=500, blank=True)
    via_type = models.CharField(max_length=100, blank=True)

    class Meta(BaseContentModel.Meta):
        verbose_name_plural = 'Testimonials'
