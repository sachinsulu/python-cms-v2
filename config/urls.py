from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.accounts.views import LoginView, LogoutView
from apps.core.views import DashboardView, HomepageView

urlpatterns = [
    # ------------------------------------------------------------------ #
    # Public
    # ------------------------------------------------------------------ #
    path("", HomepageView.as_view(), name="home"),
    # REST API v1 – public / read-only (no login required)
    path("api/", include("api.urls")),
    # Django built-in admin (keep accessible for superusers)
    path("admin/", admin.site.urls),
    # ------------------------------------------------------------------ #
    # Admin Panel  →  everything lives under /apanel/
    # ------------------------------------------------------------------ #
    path(
        "apanel/",
        include(
            [
                # Dashboard
                path("", DashboardView.as_view(), name="dashboard"),
                # Auth
                path("login/", LoginView.as_view(), name="login"),
                path("logout/", LogoutView.as_view(), name="logout"),
                # Content apps
                path("articles/", include("apps.articles.urls")),
                path("blog/", include("apps.blog.urls")),
                path("packages/", include("apps.packages.urls")),
                path("testimonials/", include("apps.testimonials.urls")),
                path("social/", include("apps.social.urls")),
                path("nearby/", include("apps.nearby.urls")),
                path("faq/", include("apps.faq.urls")),
                # Media library
                path("media-library/", include("apps.media.urls")),
                # Users & groups
                path("users/", include("apps.accounts.urls")),
                # Core – audit log + generic action endpoints
                path("core/", include("apps.core.urls")),
            ]
        ),
    ),
]

# ------------------------------------------------------------------ #
# Dev-only: serve uploaded & static files via Django
# ------------------------------------------------------------------ #
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    try:
        urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
    except Exception:
        pass
