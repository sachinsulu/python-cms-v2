from django.apps import AppConfig


class NearbyConfig(AppConfig):
    name               = 'apps.nearby'
    default_auto_field = 'django.db.models.BigAutoField'
    label              = 'nearby'

    def ready(self):
        from apps.core.registry import cms_registry, CMSModelConfig
        from .models import Nearby
        from .api import NearbyViewSet

        cms_registry.register('nearby', CMSModelConfig(
            model        = Nearby,
            stat_icon    = 'fa-solid fa-map-marker',
            stat_color   = 'blue',
            stat_perm    = 'nearby.view_nearby',
            list_url     = 'nearby_list',
            api_viewset  = NearbyViewSet,
        ))