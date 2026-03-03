from django.db import models
from apps.core.models import BaseContentModel


class Package(BaseContentModel):
    ROOM     = 'room'
    NON_ROOM = 'non_room'
    TYPE_CHOICES = [(ROOM, 'Room'), (NON_ROOM, 'Non-Room')]

    description  = models.TextField(blank=True)
    image        = models.ForeignKey(
                       'media.MediaAsset', on_delete=models.SET_NULL,
                       null=True, blank=True, related_name='packages',
                   )
    package_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=NON_ROOM)

    @property
    def is_room(self):
        return self.package_type == self.ROOM

    class Meta(BaseContentModel.Meta):
        verbose_name_plural = 'Packages'


class SubPackage(BaseContentModel):
    package     = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='sub_packages')
    description = models.TextField(blank=True)
    image       = models.ForeignKey(
                      'media.MediaAsset', on_delete=models.SET_NULL,
                      null=True, blank=True, related_name='sub_packages_media',
                  )
    price       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    capacity    = models.PositiveIntegerField(null=True, blank=True)
    beds        = models.PositiveIntegerField(null=True, blank=True)
    amenities   = models.TextField(blank=True, help_text='Comma-separated list')

    class Meta(BaseContentModel.Meta):
        verbose_name_plural = 'Sub-Packages'
