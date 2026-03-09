from django.contrib import admin
from .models import Nearby

@admin.register(Nearby)
class NearbyAdmin(admin.ModelAdmin):
    list_display = ('title', 'distance', 'is_active', 'position')
    list_filter  = ('is_active',)
    search_fields = ('title', 'content', 'distance')
    #prepopulated_fields = {'slug': ('title',)}
