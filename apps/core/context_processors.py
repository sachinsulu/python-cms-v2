from .registry import cms_registry


def cms_context(request):
    """
    Injects cms_registry into every template context.
    Templates can iterate over registered models for navigation etc.
    """
    if not request.user.is_authenticated:
        return {}
    return {
        'cms_registry': cms_registry,
    }
