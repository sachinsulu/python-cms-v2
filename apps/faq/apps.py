from django.apps import AppConfig


class FAQConfig(AppConfig):
    name               = 'apps.faq'
    default_auto_field = 'django.db.models.BigAutoField'
    label              = 'faq'

    def ready(self):
        from apps.core.registry import cms_registry, CMSModelConfig
        from .models import FAQ
        from .api import FAQViewSet

        cms_registry.register('faq', CMSModelConfig(
            model        = FAQ,
            stat_icon    = 'fa-solid fa-question',
            stat_color   = 'blue',
            stat_perm    = 'faq.view_faq',
            list_url     = 'faq_list',
            api_viewset  = FAQViewSet,
        ))