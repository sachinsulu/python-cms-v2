from django.contrib import admin
from .models import Package, SubPackage

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'package_type', 'is_active')
    list_filter  = ('package_type', 'is_active')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(SubPackage)
class SubPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'package', 'price', 'capacity', 'is_active')
    list_filter  = ('package', 'is_active')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
