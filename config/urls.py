from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views import LoginView, LogoutView
from apps.core.views import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    # Auth
    path('login/',  LoginView.as_view(),  name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Apps
    path('articles/',     include('apps.articles.urls')),
    path('blog/',         include('apps.blog.urls')),
    path('packages/',     include('apps.packages.urls')),
    path('testimonials/', include('apps.testimonials.urls')),
    path('social/',       include('apps.social.urls')),
    path('nearby/',       include('apps.nearby.urls')),

    # Users & groups
    path('users/', include('apps.accounts.urls')),

    # Core (audit log)
    path('core/', include('apps.core.urls')),

    # REST API v1
    path('api/', include('api.urls')),

    # Django admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    try:
        urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
    except Exception:
        pass
