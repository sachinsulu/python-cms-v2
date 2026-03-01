from django.apps import AppConfig


class TestimonialsConfig(AppConfig):
    name               = 'apps.testimonials'
    default_auto_field = 'django.db.models.BigAutoField'
    label              = 'testimonials'

    def ready(self):
        from apps.core.registry import cms_registry, CMSModelConfig
        from .models import Testimonial
        from .api import TestimonialViewSet

        cms_registry.register('testimonial', CMSModelConfig(
            model       = Testimonial,
            stat_icon   = 'fa-solid fa-star',
            stat_color  = 'yellow',
            stat_perm   = 'testimonials.view_testimonial',
            list_url    = 'testimonial_list',
            api_viewset = TestimonialViewSet,
        ))
