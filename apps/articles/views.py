from django.shortcuts import redirect
from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Article
from .forms import ArticleForm


class ArticleListView(ContentListView):
    model               = Article
    template            = 'articles/list.html'   # extends generic/list.html; adds homepage filter
    permission_required = 'articles.view_article'
    page_title          = 'Articles'
    create_url          = 'article_create'
    model_key           = 'article'
    edit_url_name       = 'article_edit'

    list_columns = [
        ('title',     'Title'),       # renders subtitle sub-line automatically
        ('slug',      'Slug'),
        ('author.username', 'Author'),
        ('is_active', 'Status'),
    ]

    def get_queryset(self):
        qs = Article.objects.select_related('image', 'author')
        homepage_filter = self.request.session.get('article_homepage_filter', '0')
        return qs.filter(homepage=(homepage_filter == '1'))

    def get(self, request):
        hp = request.GET.get('homepage')
        if hp in ('0', '1'):
            request.session['article_homepage_filter'] = hp
            return redirect(request.path)
        return super().get(request)

    def get_extra_context(self):
        return {'current_filter': self.request.session.get('article_homepage_filter', '0')}


class ArticleCreateView(ContentCreateView):
    model               = Article
    form_class          = ArticleForm
    permission_required = 'articles.add_article'
    
    @property
    def page_title(self):
        is_hp = self.request.session.get('article_homepage_filter') == '1'
        return 'Add Homepage Article' if is_hp else 'Add Inner Page Article'

    list_url            = 'article_list'
    edit_url            = 'article_edit'
    model_key           = 'article'

    def before_save(self, request, obj):
        obj.author   = request.user
        obj.homepage = request.session.get('article_homepage_filter') == '1'


class ArticleUpdateView(ContentUpdateView):
    model               = Article
    form_class          = ArticleForm
    permission_required = 'articles.change_article'
    
    @property
    def page_title(self):
        is_hp = self.request.session.get('article_homepage_filter') == '1'
        return 'Edit Homepage Article' if is_hp else 'Edit Inner Page Article'

    list_url            = 'article_list'
    edit_url            = 'article_edit'
    model_key           = 'article'

    def before_save(self, request, obj):
        obj.homepage = request.session.get('article_homepage_filter') == '1'