from django.apps import AppConfig


class SocialConfig(AppConfig):
    name               = 'apps.social'
    default_auto_field = 'django.db.models.BigAutoField'
    label              = 'social'

    def ready(self):
        from apps.core.registry import cms_registry, CMSModelConfig
        from .models import Social
        from .api import SocialViewSet

        cms_registry.register('social', CMSModelConfig(
            model       = Social,
            stat_icon   = 'fa-solid fa-share-nodes',
            stat_color  = 'pink',
            stat_perm   = 'social.view_social',
            list_url    = 'social_list',
            api_viewset = SocialViewSet,
            show_recent = False,
        ))
