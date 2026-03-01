from django.db import models
from apps.core.models import BaseContentModel


class Testimonial(BaseContentModel):
    BOOKING  = 'booking'
    GOOGLE   = 'google'
    DIRECT   = 'direct'
    VIA_CHOICES = [(BOOKING, 'Booking.com'), (GOOGLE, 'Google'), (DIRECT, 'Direct')]

    name     = models.CharField(max_length=255)
    content  = models.TextField()
    rating   = models.PositiveSmallIntegerField(default=5)
    image    = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    country  = models.CharField(max_length=100, blank=True)
    linksrc  = models.URLField(blank=True)
    via_type = models.CharField(max_length=20, choices=VIA_CHOICES, default=DIRECT)

    class Meta(BaseContentModel.Meta):
        verbose_name_plural = 'Testimonials'
