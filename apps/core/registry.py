"""
CMS Registry
============
Central registration system for all content models.
Each app registers itself via AppConfig.ready() — nothing is hardcoded here.
"""


class CMSModelConfig:
    """
    Configuration for a registered content model.
    Pass this to cms_registry.register() in each app's AppConfig.ready().
    """
    def __init__(
        self,
        model,
        *,
        active_field='is_active',
        supports_sort=True,
        supports_bulk=True,
        stat_icon='fa-solid fa-file',
        stat_color='blue',
        stat_perm=None,
        list_url=None,
        api_viewset=None,
        # Dashboard recent-items controls
        show_recent=True,
        recent_limit=5,
        recent_ordering='-updated_at',
    ):
        self.model           = model
        self.active_field    = active_field
        self.supports_sort   = supports_sort
        self.supports_bulk   = supports_bulk
        self.stat_icon       = stat_icon
        self.stat_color      = stat_color
        self.stat_perm       = stat_perm
        self.list_url        = list_url
        self.api_viewset     = api_viewset
        self.show_recent     = show_recent
        self.recent_limit    = recent_limit
        self.recent_ordering = recent_ordering


class CMSRegistry:
    """
    Singleton registry for all CMS content models.
    Import the module-level `cms_registry` instance — do not instantiate directly.
    """
    def __init__(self):
        self._registry: dict[str, CMSModelConfig] = {}

    def register(self, key: str, config: CMSModelConfig):
        if key in self._registry:
            raise ValueError(f"CMS model key '{key}' is already registered.")
        self._registry[key] = config

    def get(self, key: str) -> CMSModelConfig | None:
        return self._registry.get(key)

    def all(self):
        """Iterate over (key, config) pairs."""
        return self._registry.items()

    def keys(self):
        return self._registry.keys()

    # ------------------------------------------------------------------ #
    # Cross-model slug uniqueness
    # ------------------------------------------------------------------ #

    def is_slug_taken(self, slug: str, exclude_obj=None) -> bool:
        """
        Returns True if `slug` is used by any registered model.
        Pass exclude_obj when editing to skip the object being updated.
        """
        for key, config in self._registry.items():
            model = config.model
            if not hasattr(model, 'slug'):
                continue
            qs = model.objects.filter(slug=slug)
            if exclude_obj and isinstance(exclude_obj, model):
                qs = qs.exclude(pk=exclude_obj.pk)
            if qs.exists():
                return True
        return False

    # ------------------------------------------------------------------ #
    # Dashboard helpers
    # ------------------------------------------------------------------ #

    def get_dashboard_stats(self, user) -> list:
        """
        Returns stat tiles for the dashboard.
        Respects permissions — non-superusers only see what they're allowed to.
        """
        stats = []
        for key, config in self._registry.items():
            if config.stat_perm:
                if not user.is_superuser and not user.has_perm(config.stat_perm):
                    continue
            stats.append({
                'label':    key.replace('_', ' ').title(),
                'count':    config.model.objects.count(),
                'icon':     config.stat_icon,
                'color':    config.stat_color,
                'list_url': config.list_url,
            })
        return stats

    # ------------------------------------------------------------------ #
    # Dashboard recent items
    # ------------------------------------------------------------------ #

    def get_recent_items(self, user) -> dict:
        """
        Returns recent items per registered model,
        permission-aware and fully dynamic.
        """
        recent = {}

        for key, config in self._registry.items():
            if not config.show_recent:
                continue

            # Permission check
            if config.stat_perm:
                if not user.is_superuser and not user.has_perm(config.stat_perm):
                    continue

            try:
                qs = config.model.objects.order_by(config.recent_ordering)[:config.recent_limit]
                if qs.exists():
                    recent[key] = {
                        'label':    key.replace('_', ' ').title(),
                        'icon':     config.stat_icon,
                        'color':    config.stat_color,
                        'items':    qs,
                        'list_url': config.list_url,
                    }
            except Exception:
                # Fail-safe: don't break dashboard if one model errors
                continue

        return recent

    # ------------------------------------------------------------------ #
    # Generic action helpers (used by toggle/bulk/reorder views)
    # ------------------------------------------------------------------ #

    def get_model_class(self, key: str):
        config = self.get(key)
        return config.model if config else None

    def get_active_field(self, key: str) -> str | None:
        config = self.get(key)
        return config.active_field if config else None

    def supports_bulk(self, key: str) -> bool:
        config = self.get(key)
        return config.supports_bulk if config else False

    def supports_sort(self, key: str) -> bool:
        config = self.get(key)
        return config.supports_sort if config else False


# Module-level singleton — import this everywhere
cms_registry = CMSRegistry()
