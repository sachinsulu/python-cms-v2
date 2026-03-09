from django.shortcuts import redirect
from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Social
from .forms import SocialForm


class SocialListView(ContentListView):
    model               = Social
    template            = 'social/list.html'   # extends generic/list.html; adds type filter
    permission_required = 'social.view_social'
    page_title          = 'Social & OTA Links'
    create_url          = 'social_create'
    model_key           = 'social'
    edit_url_name       = 'social_edit'

    list_columns = [
        ('title',     'Title'),
        ('icon',      'Icon'),
        ('link',      'Link'),
        ('is_active', 'Status'),
    ]

    def get_queryset(self):
        type_filter = self.request.session.get('social_type_filter', Social.TYPE_SOCIAL)
        return Social.objects.select_related('image').filter(type=type_filter)

    def get(self, request):
        type_filter = request.GET.get('type')
        if type_filter in (Social.TYPE_SOCIAL, Social.TYPE_OTA):
            request.session['social_type_filter'] = type_filter
            return redirect(request.path)

        self.extra_context = {
            'current_type': request.session.get('social_type_filter', Social.TYPE_SOCIAL),
            'TYPE_SOCIAL':  Social.TYPE_SOCIAL,
            'TYPE_OTA':     Social.TYPE_OTA,
        }
        return super().get(request)


class SocialCreateView(ContentCreateView):
    model               = Social
    form_class          = SocialForm
    permission_required = 'social.add_social'
    
    @property
    def page_title(self):
        type_filter = self.request.session.get('social_type_filter', Social.TYPE_SOCIAL)
        return 'Add OTA Link' if type_filter == Social.TYPE_OTA else 'Add Social Link'

    list_url            = 'social_list'
    edit_url            = 'social_edit'
    model_key           = 'social'

    def before_save(self, request, obj):
        obj.type = request.session.get('social_type_filter', Social.TYPE_SOCIAL)


class SocialUpdateView(ContentUpdateView):
    model               = Social
    form_class          = SocialForm
    permission_required = 'social.change_social'

    @property
    def page_title(self):
        type_filter = self.request.session.get('social_type_filter', Social.TYPE_SOCIAL)
        return 'Edit OTA Link' if type_filter == Social.TYPE_OTA else 'Edit Social Link'

    list_url            = 'social_list'
    edit_url            = 'social_edit'
    model_key           = 'social'