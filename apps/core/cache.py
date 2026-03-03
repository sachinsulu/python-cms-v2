from django.core.cache import cache

def invalidate_dashboard_cache():
    """Bump the version key so all per-user stat caches are skipped.
    Old keys auto-expire via their 60s timeout set in DashboardView."""
    try:
        cache.incr('dashboard_stats_version')
    except ValueError:
        cache.set('dashboard_stats_version', 2, timeout=None)
