from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'rating', 'via_type', 'is_active')
    list_filter  = ('rating', 'is_active')
    search_fields = ('title', 'name', 'content')
    prepopulated_fields = {'slug': ('title',)}
