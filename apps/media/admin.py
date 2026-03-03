from django.contrib import admin
from django.utils.html import format_html
from .models import MediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display  = ['preview_thumb', 'file', 'file_type', 'alt_text', 'width', 'height', 'uploaded_by', 'created_at']
    list_filter   = ['file_type', 'created_at']
    search_fields = ['file', 'alt_text']
    readonly_fields = ['width', 'height', 'file_type', 'thumbnail', 'preview_large']

    def preview_thumb(self, obj):
        if obj.is_image and obj.file:
            url = obj.thumbnail_url
            return format_html('<img src="{}" style="max-height:40px; border-radius:4px;" />', url)
        return '—'
    preview_thumb.short_description = 'Preview'

    def preview_large(self, obj):
        if obj.is_image and obj.file:
            return format_html('<img src="{}" style="max-width:400px;" />', obj.url)
        return '—'
    preview_large.short_description = 'Full Preview'
