from django import forms
from .models import Nearby

class NearbyForm(forms.ModelForm):
    class Meta:
        model  = Nearby
        fields = ['title', 'map_link', 'distance', 'content', 'is_active']
        labels = {
            'is_active': 'Active'
        }
        widgets = {
            'title':    forms.TextInput(attrs={'placeholder': 'e.g. Nearby Beach, City Center'}),
            # URLInput renders <input type="url"> — native browser URL
            # validation on mobile and consistent with the URLField type.
            'map_link': forms.URLInput(attrs={
                'placeholder': 'https://maps.google.com/?q=...',
            }),
            'distance': forms.TextInput(attrs={'placeholder': 'e.g. 500m, 10 mins walk'}),
            'content':  forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief description'}),
        }
