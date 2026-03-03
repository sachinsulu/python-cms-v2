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
        # Pure — reads session but never writes it
        type_filter = self.request.session.get('social_type_filter', Social.TYPE_SOCIAL)
        return Social.objects.select_related('image').filter(type=type_filter)

    def get(self, request):
        # Only place that writes the session
        type_filter = request.GET.get('type')
        if type_filter in (Social.TYPE_SOCIAL, Social.TYPE_OTA):
            request.session['social_type_filter'] = type_filter

        self.extra_context = {
            'current_type': request.session.get('social_type_filter', Social.TYPE_SOCIAL),
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
