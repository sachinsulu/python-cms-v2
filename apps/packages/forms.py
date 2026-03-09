from django import forms
from apps.media.widgets import MediaPickerWidget
from .models import Package, SubPackage


class PackageForm(forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model  = Package
        fields = ['title', 'slug', 'description', 'image', 'package_type', 'is_active',
                  'meta_title', 'meta_description', 'meta_keywords']
        labels = {
            'is_active': 'Active'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'image':       MediaPickerWidget(),
        }


class SubPackageForm(forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model  = SubPackage
        fields = ['title', 'slug', 'description', 'image', 'price',
                  'capacity', 'beds', 'amenities', 'is_active',
                  'meta_title', 'meta_description', 'meta_keywords']
        labels = {
            'is_active': 'Active'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amenities':   forms.Textarea(attrs={'rows': 3, 'placeholder': 'WiFi, Pool, Breakfast'}),
            'image':       MediaPickerWidget(),
        }
