from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Social
from .forms import SocialForm


class SocialListView(ContentListView):
    template            = 'social/list.html'
    model               = Social
    permission_required = 'social.view_social'
    page_title          = 'Social & OTA Links'
    create_url          = 'social_create'
    model_key           = 'social'

    def get_queryset(self):
        filter = self.request.GET.get('type', Social.TYPE_SOCIAL)
        self.request.session['social_type_filter'] = filter
        return Social.objects.filter(type=filter)

    def get(self, request):
        filter = request.GET.get('type', request.session.get('social_type_filter', Social.TYPE_SOCIAL))
        self.extra_context = {
            'current_type': filter,
            'TYPE_SOCIAL':  Social.TYPE_SOCIAL,
            'TYPE_OTA':     Social.TYPE_OTA,
        }
        return super().get(request)


class SocialCreateView(ContentCreateView):
    template            = 'social/form.html'
    model               = Social
    form_class          = SocialForm
    permission_required = 'social.add_social'
    page_title          = 'Add Social / OTA Link'
    list_url            = 'social_list'
    edit_url            = 'social_edit'

    def before_save(self, request, obj):
        obj.type = request.session.get('social_type_filter', Social.TYPE_SOCIAL)


class SocialUpdateView(ContentUpdateView):
    template            = 'social/form.html'
    model               = Social
    form_class          = SocialForm
    permission_required = 'social.change_social'
    page_title          = 'Edit Social / OTA Link'
    list_url            = 'social_list'
    edit_url            = 'social_edit'
