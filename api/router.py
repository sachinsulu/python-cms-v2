"""
API Router
==========
Auto-wires all registered ViewSets from the CMS registry.
Adding a new content type with an api_viewset automatically gets an endpoint here.
"""
from rest_framework.routers import DefaultRouter


def build_router():
    """Build lazily — registry is populated after AppConfig.ready() fires."""
    from apps.core.registry import cms_registry
    from apps.packages.api import SubPackageViewSet  # registered separately

    router = DefaultRouter()

    for key, config in cms_registry.all():
        if config.api_viewset:
            router.register(f'{key}s', config.api_viewset, basename=key)

    return router
