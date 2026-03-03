from django.apps import AppConfig


class MediaConfig(AppConfig):
    name               = 'apps.media'
    default_auto_field = 'django.db.models.BigAutoField'
    label              = 'media'

    def ready(self):
        from apps.core.registry import cms_registry, CMSModelConfig
        from .models import MediaAsset

        cms_registry.register('media', CMSModelConfig(
            model=MediaAsset,
            active_field='is_active',
            supports_sort=False,
            supports_bulk=True,
            stat_icon='fa-solid fa-images',
            stat_color='purple',
            stat_perm='media.view_mediaasset',
            list_url='media_admin_list',
            api_viewset=None,
            show_recent=True,
            recent_limit=8,
            recent_ordering='-created_at',
        ))
