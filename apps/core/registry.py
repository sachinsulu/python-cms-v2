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

    parent_field (optional):
        Name of the ForeignKey field that scopes instances to a parent object.
        Example: 'package' on SubPackage.

        When set, the generic update_order view restricts its reorder queryset
        to objects sharing the same parent as the first item in the payload.
        This prevents a malicious or accidental payload from reassigning
        positions across different parent objects.

        Leave as None (the default) for all top-level models — behaviour is
        identical to before this field was introduced.
    """

    def __init__(
        self,
        model,
        *,
        active_field="is_active",
        supports_sort=True,
        supports_bulk=True,
        stat_icon="fa-solid fa-file",
        stat_color="blue",
        stat_perm=None,
        list_url=None,
        api_viewset=None,
        # Dashboard recent-items controls
        show_recent=True,
        recent_limit=5,
        recent_ordering="-updated_at",
        # Parent-scoped ordering (e.g. SubPackage → Package)
        parent_field=None,
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
        self.parent_field    = parent_field

    def __repr__(self) -> str:
        return (
            f"CMSModelConfig(model={self.model.__name__!r}, "
            f"list_url={self.list_url!r}, "
            f"active_field={self.active_field!r})"
        )

    def __str__(self) -> str:
        return f"CMSModelConfig<{self.model.__name__}>"


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
        if not hasattr(config.model, "_meta"):
            raise TypeError(
                f"config.model for key '{key}' does not appear to be a Django model. "
                f"Got: {config.model!r}"
            )
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
        Returns True if slug is already registered in GlobalSlug.
        Delegates to apps.core.services.slug_service for the pure logic.
        """
        from apps.core.services.slug_service import is_slug_taken

        return is_slug_taken(slug, exclude_obj=exclude_obj)

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
            stats.append(
                {
                    "label":    key.replace("_", " ").title(),
                    "count":    config.model.objects.active().count(),
                    "icon":     config.stat_icon,
                    "color":    config.stat_color,
                    "list_url": config.list_url,
                }
            )
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
                # Materialise to a list so we pay exactly one DB query.
                # qs.exists() would be a second round-trip; list() is not.
                items = list(
                    config.model.objects
                    .order_by(config.recent_ordering)[: config.recent_limit]
                )
                if items:
                    recent[key] = {
                        "label":    key.replace("_", " ").title(),
                        "icon":     config.stat_icon,
                        "color":    config.stat_color,
                        "items":    items,
                        "list_url": config.list_url,
                    }
            except Exception:
                # Fail-safe: don't break the dashboard if one model errors.
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


# Module-level singleton — import this everywhere.
cms_registry = CMSRegistry()