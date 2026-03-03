from django import forms
from django.conf import settings
from apps.media.widgets import MediaPickerWidget
from .models import Article


class ArticleForm(forms.ModelForm):
    slug = forms.SlugField(
        required=False,
        help_text='Auto-generated from title. Edit if needed.',
    )

    class Meta:
        model  = Article
        fields = [
            'title', 'subtitle', 'slug', 'content', 'image',
            'meta_title', 'meta_description', 'meta_keywords',
        ]
        widgets = {
            'title':    forms.TextInput(attrs={'placeholder': 'Article title'}),
            'subtitle': forms.TextInput(attrs={'placeholder': 'Optional subtitle'}),
            'content':  forms.Textarea(attrs={'rows': 16}),
            'image':    MediaPickerWidget(),
        }
