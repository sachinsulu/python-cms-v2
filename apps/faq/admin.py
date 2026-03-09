from django.contrib import admin
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'is_active', 'position')
    list_filter  = ('is_active',)
    search_fields = ('title', 'content')
    #prepopulated_fields = {'slug': ('title',)}