from django import forms
from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model  = Testimonial
        fields = ['title', 'name', 'content', 'rating', 'image',
                  'country', 'linksrc', 'via_type',
                  'meta_title', 'meta_description', 'meta_keywords']
        widgets = {
            'title':   forms.TextInput(attrs={'placeholder': 'Review title'}),
            'name':    forms.TextInput(attrs={'placeholder': 'Reviewer name'}),
            'content': forms.Textarea(attrs={'rows': 6}),
            'rating':  forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
