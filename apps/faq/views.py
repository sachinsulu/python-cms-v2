from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import FAQ
from .forms import FAQForm


class FAQListView(ContentListView):
    model               = FAQ
    permission_required = 'faq.view_faq'
    page_title          = 'FAQ'
    create_url          = 'faq_create'
    model_key           = 'faq'
    edit_url_name       = 'faq_edit'

    list_columns = [
        ('title',    'Title'),
        ('is_active','Status'),
    ]


class FAQCreateView(ContentCreateView):
    model               = FAQ
    form_class          = FAQForm
    permission_required = 'faq.add_faq'
    page_title          = 'Add FAQ'
    list_url            = 'faq_list'
    edit_url            = 'faq_edit'
    model_key           = 'faq'


class FAQUpdateView(ContentUpdateView):
    model               = FAQ
    form_class          = FAQForm
    permission_required = 'faq.change_faq'
    page_title          = 'Edit FAQ'
    list_url            = 'faq_list'
    edit_url            = 'faq_edit'
    model_key           = 'faq'