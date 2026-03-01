from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Blog
from .forms import BlogForm


class BlogListView(ContentListView):
    template            = 'blog/list.html'
    model               = Blog
    permission_required = 'blog.view_blog'
    page_title          = 'Blog Posts'
    create_url          = 'blog_create'
    model_key           = 'blog'


class BlogCreateView(ContentCreateView):
    template            = 'blog/form.html'
    model               = Blog
    form_class          = BlogForm
    permission_required = 'blog.add_blog'
    page_title          = 'Add Blog Post'
    list_url            = 'blog_list'
    edit_url            = 'blog_edit'

    def before_save(self, request, obj):
        obj.author = request.user


class BlogUpdateView(ContentUpdateView):
    template            = 'blog/form.html'
    model               = Blog
    form_class          = BlogForm
    permission_required = 'blog.change_blog'
    page_title          = 'Edit Blog Post'
    list_url            = 'blog_list'
    edit_url            = 'blog_edit'
