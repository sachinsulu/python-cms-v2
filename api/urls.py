from django.urls import path, include
from .router import build_router

# Build lazily so AppConfig.ready() has already fired
def get_urlpatterns():
    router = build_router()
    return [path('v1/', include(router.urls))]

urlpatterns = get_urlpatterns()
