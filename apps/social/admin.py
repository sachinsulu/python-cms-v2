from django.contrib import admin
from .models import Social

@admin.register(Social)
class SocialAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'is_active')
    list_filter  = ('type', 'is_active')
    search_fields = ('title', 'link')
    prepopulated_fields = {'slug': ('title',)}
    exclude = ('meta_title', 'meta_description', 'meta_keywords')
