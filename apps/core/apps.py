from django.apps import AppConfig


class CoreConfig(AppConfig):
    name           = 'apps.core'
    default_auto_field = 'django.db.models.BigAutoField'
    label          = 'core'

    def ready(self):
        # Core doesn't register content models — it IS the registry.
        import apps.core.signals

        # Connect the GlobalSlug cleanup signal only to concrete
        # BaseContentModel subclasses instead of every model in the project.
        #
        # Why here instead of models.py?
        #   ready() runs after all AppConfigs have been imported and all
        #   models are registered, so django_apps.get_models() returns the
        #   complete set.  Connecting in models.py with a bare @receiver(post_delete)
        #   fires on every single delete in the project — User, Permission,
        #   Session, MediaAsset, etc. — paying the isinstance() guard cost
        #   every time even though only BaseContentModel subclasses ever have
        #   a slug to clean up.
        from django.apps import apps as django_apps
        from django.db.models.signals import post_delete
        from .models import BaseContentModel, _remove_global_slug

        for model in django_apps.get_models():
            if (
                issubclass(model, BaseContentModel)
                and not model._meta.abstract
            ):
                post_delete.connect(
                    _remove_global_slug,
                    sender=model,
                    dispatch_uid=f"remove_global_slug_{model._meta.label}",
                )
