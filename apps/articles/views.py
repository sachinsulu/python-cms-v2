from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Article
from .forms import ArticleForm


class ArticleListView(ContentListView):
    model               = Article
    template            = 'articles/list.html'
    permission_required = 'articles.view_article'
    page_title          = 'Articles'
    create_url          = 'article_create'
    model_key           = 'article'

    def get_queryset(self):
        qs     = super().get_queryset()
        filter = self.request.session.get('article_homepage_filter', '0')
        return qs.filter(homepage=(filter == '1'))

    def get(self, request):
        # Persist homepage filter in session
        hp = request.GET.get('homepage')
        if hp in ('0', '1'):
            request.session['article_homepage_filter'] = hp
        return super().get(request)

    def get_extra_context(self):
        return {'current_filter': self.request.session.get('article_homepage_filter', '0')}


class ArticleCreateView(ContentCreateView):
    model               = Article
    form_class          = ArticleForm
    permission_required = 'articles.add_article'
    page_title          = 'Add Article'
    list_url            = 'article_list'
    edit_url            = 'article_edit'

    def before_save(self, request, obj):
        obj.author   = request.user
        obj.homepage = request.session.get('article_homepage_filter') == '1'


class ArticleUpdateView(ContentUpdateView):
    model               = Article
    form_class          = ArticleForm
    permission_required = 'articles.change_article'
    page_title          = 'Edit Article'
    list_url            = 'article_list'
    edit_url            = 'article_edit'

    def before_save(self, request, obj):
        obj.homepage = request.session.get('article_homepage_filter') == '1'
