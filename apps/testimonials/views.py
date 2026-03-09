from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Testimonial
from .forms import TestimonialForm


class TestimonialListView(ContentListView):
    model               = Testimonial
    permission_required = 'testimonials.view_testimonial'
    page_title          = 'Testimonials'
    create_url          = 'testimonial_create'
    model_key           = 'testimonial'
    edit_url_name       = 'testimonial_edit'

    list_columns = [
        ('title',    'Title'),    # renders 'name' sub-line automatically (no subtitle field)
        ('rating',   'Rating'),
        ('via_type', 'Via'),
        ('is_active','Status'),
    ]

    def get_queryset(self):
        return Testimonial.objects.select_related('image').all()


class TestimonialCreateView(ContentCreateView):
    model               = Testimonial
    form_class          = TestimonialForm
    permission_required = 'testimonials.add_testimonial'
    page_title          = 'Add Testimonial'
    list_url            = 'testimonial_list'
    edit_url            = 'testimonial_edit'
    model_key           = 'testimonial'


class TestimonialUpdateView(ContentUpdateView):
    model               = Testimonial
    form_class          = TestimonialForm
    permission_required = 'testimonials.change_testimonial'
    page_title          = 'Edit Testimonial'
    list_url            = 'testimonial_list'
    edit_url            = 'testimonial_edit'
    model_key           = 'testimonial'