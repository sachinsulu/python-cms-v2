from django import forms
from .models import Social


class SocialForm(forms.ModelForm):
    remove_image = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')

    class Meta:
        model  = Social
        fields = ['title', 'link', 'image', 'icon']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Instagram'}),
            'link':  forms.TextInput(attrs={'placeholder': 'Enter social link or reference'}),
            'icon':  forms.TextInput(attrs={'placeholder': 'fa-brands fa-instagram'}),
        }
