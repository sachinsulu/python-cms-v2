from django import forms
from apps.media.widgets import MediaPickerWidget
from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model  = Testimonial
        fields = ['title', 'name', 'content', 'rating', 'image', 'is_active',
                  'country', 'linksrc', 'via_type']
        labels = {
            'is_active': 'Active'
        }
        widgets = {
            'title':    forms.TextInput(attrs={'placeholder': 'Review title'}),
            'name':     forms.TextInput(attrs={'placeholder': 'Reviewer name'}),
            'content':  forms.Textarea(attrs={'rows': 6}),
            'rating':   forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'via_type': forms.TextInput(attrs={'placeholder': 'e.g. Booking, Google, Direct'}),
            'linksrc':  forms.TextInput(attrs={'placeholder': 'Source URL or reference link'}),
            'image':    MediaPickerWidget(),
        }
