from django import forms
from apps.media.widgets import MediaPickerWidget
from .models import Social


class SocialForm(forms.ModelForm):
    class Meta:
        model  = Social
        fields = ['title', 'link', 'image', 'icon', 'is_active']
        labels = {
            'is_active': 'Active'
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Instagram'}),
            'link':  forms.TextInput(attrs={'placeholder': 'Enter social link or reference'}),
            'icon':  forms.TextInput(attrs={'placeholder': 'fa-brands fa-instagram'}),
            'image': MediaPickerWidget(),
        }
