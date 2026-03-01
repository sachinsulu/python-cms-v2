from django.db import models
from apps.core.models import BaseContentModel


class Social(BaseContentModel):
    TYPE_SOCIAL = 'social'
    TYPE_OTA    = 'ota'
    TYPE_CHOICES = [(TYPE_SOCIAL, 'Social Media'), (TYPE_OTA, 'OTA / Booking')]

    link  = models.URLField()
    image = models.ImageField(upload_to='social/', blank=True, null=True)
    icon  = models.CharField(max_length=100, blank=True,
                help_text='Font Awesome class e.g. fa-brands fa-instagram')
    type  = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_SOCIAL, db_index=True)

    class Meta(BaseContentModel.Meta):
        verbose_name_plural = 'Social / OTA Links'
