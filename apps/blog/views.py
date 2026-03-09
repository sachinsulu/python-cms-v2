from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Blog
from .forms import BlogForm


class BlogListView(ContentListView):
    model               = Blog
    permission_required = 'blog.view_blog'
    page_title          = 'Blog Posts'
    create_url          = 'blog_create'
    model_key           = 'blog'
    edit_url_name       = 'blog_edit'

    list_columns = [
        ('title',          'Title'),      # renders subtitle sub-line automatically
        ('slug',           'Slug'),
        ('author.username','Author'),
        ('date',           'Date'),
        ('is_active',      'Status'),
    ]

    def get_queryset(self):
        return Blog.objects.select_related('image', 'banner_image', 'author').all()


class BlogCreateView(ContentCreateView):
    model               = Blog
    form_class          = BlogForm
    permission_required = 'blog.add_blog'
    page_title          = 'Add Blog Post'
    list_url            = 'blog_list'
    edit_url            = 'blog_edit'
    model_key           = 'blog'

    def before_save(self, request, obj):
        obj.author = request.user


class BlogUpdateView(ContentUpdateView):
    model               = Blog
    form_class          = BlogForm
    permission_required = 'blog.change_blog'
    page_title          = 'Edit Blog Post'
    list_url            = 'blog_list'
    edit_url            = 'blog_edit'
    model_key           = 'blog'