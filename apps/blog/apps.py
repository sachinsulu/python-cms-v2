from django.apps import AppConfig


class BlogConfig(AppConfig):
    name               = 'apps.blog'
    default_auto_field = 'django.db.models.BigAutoField'
    label              = 'blog'

    def ready(self):
        from apps.core.registry import cms_registry, CMSModelConfig
        from .models import Blog
        from .api import BlogViewSet

        cms_registry.register('blog', CMSModelConfig(
            model       = Blog,
            stat_icon   = 'fa-solid fa-blog',
            stat_color  = 'orange',
            stat_perm   = 'blog.view_blog',
            list_url    = 'blog_list',
            api_viewset = BlogViewSet,
        ))
