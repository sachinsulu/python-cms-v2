from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Testimonial
from .forms import TestimonialForm


class TestimonialListView(ContentListView):
    template            = 'testimonials/list.html'
    model               = Testimonial
    permission_required = 'testimonials.view_testimonial'
    page_title          = 'Testimonials'
    create_url          = 'testimonial_create'
    model_key           = 'testimonial'


class TestimonialCreateView(ContentCreateView):
    template            = 'testimonials/form.html'
    model               = Testimonial
    form_class          = TestimonialForm
    permission_required = 'testimonials.add_testimonial'
    page_title          = 'Add Testimonial'
    list_url            = 'testimonial_list'
    edit_url            = 'testimonial_edit'


class TestimonialUpdateView(ContentUpdateView):
    template            = 'testimonials/form.html'
    model               = Testimonial
    form_class          = TestimonialForm
    permission_required = 'testimonials.change_testimonial'
    page_title          = 'Edit Testimonial'
    list_url            = 'testimonial_list'
    edit_url            = 'testimonial_edit'
