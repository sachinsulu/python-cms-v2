from django import forms
from .models import Nearby

class NearbyForm(forms.ModelForm):
    class Meta:
        model  = Nearby
        fields = ['title', 'map_link', 'distance', 'content']
        widgets = {
            'title':    forms.TextInput(attrs={'placeholder': 'e.g. Nearby Beach, City Center'}),
            'map_link': forms.TextInput(attrs={'placeholder': 'Google Maps URL'}),
            'distance': forms.TextInput(attrs={'placeholder': 'e.g. 500m, 10 mins walk'}),
            'content':  forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief description'}),
        }
