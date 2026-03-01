from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Nearby
from .forms import NearbyForm

class NearbyListView(ContentListView):
    model               = Nearby
    template            = 'nearby/list.html'
    permission_required = 'nearby.view_nearby'
    page_title          = 'Nearby'
    create_url          = 'nearby_create'
    model_key           = 'nearby'


class NearbyCreateView(ContentCreateView):
    model               = Nearby
    form_class          = NearbyForm
    permission_required = 'nearby.add_nearby'
    page_title          = 'Add Nearby Place'
    list_url            = 'nearby_list'
    edit_url            = 'nearby_edit'
    model_key           = 'nearby'


class NearbyUpdateView(ContentUpdateView):
    model               = Nearby
    form_class          = NearbyForm
    permission_required = 'nearby.change_nearby'
    page_title          = 'Edit Nearby Place'
    list_url            = 'nearby_list'
    edit_url            = 'nearby_edit'
    model_key           = 'nearby'
