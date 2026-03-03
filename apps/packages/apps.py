from django.apps import AppConfig


class PackagesConfig(AppConfig):
    name               = 'apps.packages'
    default_auto_field = 'django.db.models.BigAutoField'
    label              = 'packages'

    def ready(self):
        from apps.core.registry import cms_registry, CMSModelConfig
        from .models import Package, SubPackage
        from .api import PackageViewSet, SubPackageViewSet

        cms_registry.register('package', CMSModelConfig(
            model       = Package,
            stat_icon   = 'fa-solid fa-box',
            stat_color  = 'green',
            stat_perm   = 'packages.view_package',
            list_url    = 'package_list',
            api_viewset = PackageViewSet,
        ))
        cms_registry.register('subpackage', CMSModelConfig(
            model       = SubPackage,
            stat_icon   = 'fa-solid fa-boxes-stacked',
            stat_color  = 'cyan',
            stat_perm   = 'packages.view_subpackage',
            list_url    = None,
            api_viewset = SubPackageViewSet,
            show_recent = False,
        ))
