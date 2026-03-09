from django import forms
from .models import FAQ

class FAQForm(forms.ModelForm):
    class Meta:
        model  = FAQ
        fields = ['title', 'content', 'is_active']
        labels = {
            'is_active': 'Active'
        }
        widgets = {
            'title':    forms.TextInput(attrs={'placeholder': 'e.g. FAQ Title'}),
            'content':  forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief description'}),
        }