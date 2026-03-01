from django.apps import AppConfig


class CoreConfig(AppConfig):
    name           = 'apps.core'
    default_auto_field = 'django.db.models.BigAutoField'
    label          = 'core'

    def ready(self):
        # Core doesn't register content models — it IS the registry.
        import apps.core.signals
