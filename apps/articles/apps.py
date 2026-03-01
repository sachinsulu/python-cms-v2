from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    name               = 'apps.articles'
    default_auto_field = 'django.db.models.BigAutoField'
    label              = 'articles'

    def ready(self):
        from apps.core.registry import cms_registry, CMSModelConfig
        from .models import Article
        from .api import ArticleViewSet

        cms_registry.register('article', CMSModelConfig(
            model        = Article,
            stat_icon    = 'fa-solid fa-newspaper',
            stat_color   = 'blue',
            stat_perm    = 'articles.view_article',
            list_url     = 'article_list',
            api_viewset  = ArticleViewSet,
        ))
