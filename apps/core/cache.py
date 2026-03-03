from django.core.cache import cache

def invalidate_dashboard_cache():
    """Bump the version key so all per-user stat caches are skipped."""
    version = cache.get('dashboard_stats_version', 1)
    cache.set('dashboard_stats_version', version + 1, timeout=None)
